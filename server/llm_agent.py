from typing import TypedDict, Optional
import json
from langgraph.graph import StateGraph, END
from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from config import logger, CONFIG

class AgentState(TypedDict):
    query: str
    plan: Optional[dict]
    document_results: Optional[str]
    sql_query: Optional[str]
    db_results: Optional[list]
    final_response: Optional[str]
    completion_status: Optional[dict]

class QueryAgent:
    def __init__(self, db_manager, vector_store):
        self.db_manager = db_manager
        self.vector_store = vector_store
        self.llm = ChatGroq(model="llama-3.3-70b-versatile", api_key=CONFIG["GROQ_API_KEY"])
        self.parser = StrOutputParser()
        logger.info("LLM initialized")
        print("Step: LLM initialized")
        self.workflow = self._build_workflow()
        logger.info("Agent initialized")

    def _plan_query_strategy(self, state: AgentState) -> AgentState:
        print("Step: Planning query strategy...")
        prompt = ChatPromptTemplate.from_template(
            """
            You are a data analyst planning how to answer a query using a PostgreSQL database and a document repository.
            Provide a JSON plan with:
            {
                "intent": "document" | "data" | "hybrid",
                "approach": "db_first" | "doc_first" | "none",
                "db_query": string,
                "doc_query": string
            }
            - intent: 'document' (document-based), 'data' (database-based), or 'hybrid' (both).
            - approach: For 'hybrid', specify 'db_first' or 'doc_first'; use 'none' for 'document' or 'data'.
            - db_query: Sub-query for the database (e.g., "Count of basket sales in Kolkata") or "" if not applicable.
            - doc_query: Sub-query for documents (e.g., "Kolkata sales in winter season") or "" if not applicable.
            For complex queries, split into db and doc sub-queries based on the schema and context.
            If unable to plan, use default:
            {
                "intent": "data",
                "approach": "none",
                "db_query": "{query}",
                "doc_query": ""
            }
            Return the JSON object as a string, without ```json or other wrappers.
            Schema: {schema}
            Query: {query}
            """
        )
        try:
            schema = self.db_manager.get_schema()
            chain = prompt | self.llm | self.parser
            plan_json = chain.invoke({"query": state["query"], "schema": schema}).strip()
            state["plan"] = json.loads(plan_json)
            required_keys = {"intent", "approach", "db_query", "doc_query"}
            if not all(k in state["plan"] for k in required_keys) or state["plan"]["intent"] not in ["document", "data", "hybrid"]:
                raise ValueError("Invalid plan structure")
            logger.info(f"Query plan: {state['plan']}")
            print(f"Step: Plan created: {state['plan']['intent']}, {state['plan']['approach']}")
        except Exception as e:
            logger.error(f"Error planning query: {e}")
            print(f"Step: Planning error: {e}")
            state["plan"] = {
                "intent": "data",
                "approach": "none",
                "db_query": state["query"],
                "doc_query": ""
            }
            logger.info(f"Default plan used: {state['plan']}")
            print("Step: Using default plan")
        return state

    def _query_database(self, state: AgentState) -> AgentState:
        if state["plan"]["intent"] not in ["data", "hybrid"] or not state["plan"]["db_query"]:
            print("Step: Querying database... (Skipped)")
            return state
        if state["plan"]["intent"] == "hybrid" and state["plan"]["approach"] == "doc_first" and not state["document_results"]:
            print("Step: Querying database... (Waiting for documents)")
            return state
        print("Step: Querying database...")
        try:
            schema = self.db_manager.get_schema()
            prompt = ChatPromptTemplate.from_template(
                """
                You are a PostgreSQL expert. Write a single, executable SQL query to answer the database sub-query.
                - Use the schema to identify relevant tables and columns.
                - Focus on the sub-query: {db_query}.
                - Return ONLY the SQL query, no explanations, comments, or backticks.
                - If no relevant tables/columns are found, return an empty string.
                Schema: {schema}
                Document Info: {doc_results}
                Plan: {plan}
                """
            )
            chain = prompt | self.llm | self.parser
            sql_query = chain.invoke({
                "schema": schema,
                "doc_results": state["document_results"] or "None",
                "db_query": state["plan"]["db_query"],
                "plan": json.dumps(state["plan"])
            }).strip()
            if not sql_query:
                logger.error("No valid SQL query generated")
                state["final_response"] = "Error: No valid SQL query generated for the database sub-query."
                print("Step: SQL generation failed")
                return state
            state["sql_query"] = sql_query
            state["db_results"] = self.db_manager.execute_query(sql_query)
            logger.info(f"SQL query executed: {sql_query}")
            print(f"Step: Database results: {state['db_results']}")
        except Exception as e:
            logger.error(f"Error querying database: {e}")
            state["final_response"] = f"Error querying database: {str(e)}. Unable to retrieve data."
            print("Step: Database query failed")
        return state

    def _query_documents(self, state: AgentState) -> AgentState:
        if state["plan"]["intent"] not in ["document", "hybrid"] or not state["plan"]["doc_query"]:
            print("Step: Querying documents... (Skipped)")
            return state
        if state["plan"]["intent"] == "hybrid" and state["plan"]["approach"] == "db_first" and not state["db_results"]:
            print("Step: Querying documents... (Waiting for database)")
            return state
        print("Step: Querying documents...")
        try:
            docs = self.vector_store.similarity_search(state["plan"]["doc_query"], k=3)
            doc_content = "\n".join([doc.page_content for doc in docs])
            prompt = ChatPromptTemplate.from_template(
                """
                You are a data analyst. Summarize information from the documents to answer the document sub-query.
                - Focus on the sub-query: {doc_query}.
                - Provide a concise summary (2-3 sentences).
                - If no relevant information is found, return: "No relevant document information found."
                Documents: {documents}
                Plan: {plan}
                """
            )
            chain = prompt | self.llm | self.parser
            state["document_results"] = chain.invoke({
                "doc_query": state["plan"]["doc_query"],
                "documents": doc_content,
                "plan": json.dumps(state["plan"])
            })
            logger.info("Documents queried")
            print(f"Step: Retrieved {len(docs)} documents")
        except Exception as e:
            logger.error(f"Error querying documents: {e}")
            state["document_results"] = "No relevant document information found."
            print("Step: Document query failed")
        return state

    def _check_completion(self, state: AgentState) -> AgentState:
        print("Step: Checking completion...")
        prompt = ChatPromptTemplate.from_template(
            """
            You are a data analyst reviewing query resolution against the plan. Determine if the query is fully answered.
            - Plan: {plan}
            - Query: {query}
            - Database Results: {db_results}
            - Document Results: {doc_results}
            Return a JSON object as a string with:
            - completed: Boolean (true if both db_query and doc_query are answered per plan, false if not).
            - remaining: String describing what's missing (e.g., "Database sub-query not answered") or "None" if complete.
            - action: String ("db_query", "doc_query", "none") for next step if incomplete.
            If unsure, default to:
            {
                "completed": true,
                "remaining": "None",
                "action": "none"
            }
            Return the JSON object as a string, without ```json or other wrappers.
            """
        )
        try:
            chain = prompt | self.llm | self.parser
            completion_json = chain.invoke({
                "query": state["query"],
                "plan": json.dumps(state["plan"]),
                "db_results": str(state["db_results"]) or "None",
                "doc_results": state["document_results"] or "None"
            }).strip()
            state["completion_status"] = json.loads(completion_json)
            logger.info(f"Completion status: {state['completion_status']}")
            print(f"Step: Completion: {state['completion_status']['completed']}, Action: {state['completion_status']['action']}")
        except Exception as e:
            logger.error(f"Error checking completion: {e}")
            state["completion_status"] = {
                "completed": True,
                "remaining": "None",
                "action": "none"
            }
            print(f"Step: Completion check failed: {e}")
        return state

    def _generate_final_response(self, state: AgentState) -> AgentState:
        print("Step: Generating final response...")
        try:
            schema = self.db_manager.get_schema()
            prompt = ChatPromptTemplate.from_template(
                """
                You are a data analyst. Provide a concise, professional response to the query using outputs from all nodes.
                - Use database results for numerical or factual answers.
                - Include document information (1-2 sentences) if relevant.
                - If incomplete (per completion status), note what's missing and suggest rephrasing.
                - If an error occurred, explain it clearly using the error message in final_response.
                Schema: {schema}
                Query: {query}
                Plan: {plan}
                Database Results: {db_results}
                Document Results: {doc_results}
                Completion Status: {completion_status}
                """
            )
            chain = prompt | self.llm | self.parser
            state["final_response"] = chain.invoke({
                "schema": schema,
                "query": state["query"],
                "plan": json.dumps(state["plan"]),
                "db_results": str(state["db_results"]) or "None",
                "doc_results": state["document_results"] or "None",
                "completion_status": json.dumps(state["completion_status"])
            })
            logger.info("Final response generated")
            print("Step: Response generated")
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            state["final_response"] = f"Error generating response: {str(e)}. Unable to answer."
            print("Step: Response generation failed")
        return state

    def _build_workflow(self):
        workflow = StateGraph(AgentState)
        workflow.add_node("plan_query_strategy", self._plan_query_strategy)
        workflow.add_node("query_database", self._query_database)
        workflow.add_node("query_documents", self._query_documents)
        workflow.add_node("check_completion", self._check_completion)
        workflow.add_node("generate_final_response", self._generate_final_response)

        workflow.set_entry_point("plan_query_strategy")
        workflow.add_edge("plan_query_strategy", "query_database")
        workflow.add_edge("query_database", "query_documents")
        workflow.add_edge("query_documents", "check_completion")
        workflow.add_conditional_edges(
            "check_completion",
            lambda state: state["completion_status"]["action"] if state.get("completion_status") else "none",
            {
                "db_query": "query_database",
                "doc_query": "query_documents",
                "none": "generate_final_response"
            }
        )
        workflow.add_edge("generate_final_response", END)
        return workflow.compile()

    def execute_query(self, query: str):
        print(f"\n=== Query: '{query}' ===")
        state = AgentState(
            query=query,
            plan=None,
            document_results=None,
            sql_query=None,
            db_results=None,
            final_response=None,
            completion_status=None
        )
        try:
            result = self.workflow.invoke(state)
            print(f"\nFinal Answer: {result['final_response']}")
            print("=== Query Completed ===")
            return result["final_response"]
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            print("Step: Query execution failed")
            return f"Error: Query execution failed: {str(e)}"