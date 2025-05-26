from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from llm_models import BedrockLanguageModel
from database import DatabaseManager
from config import CONFIG, logger

class DatabaseQuery:
    def __init__(self, db_manager: DatabaseManager):
        try:
            self.db_manager = db_manager
            self.llm = BedrockLanguageModel(api_key=CONFIG["ANTHROPIC_API_KEY"], model_id="claude-3.5-sonnet")
            self.parser = StrOutputParser()
            logger.info("DatabaseQuery initialized")
        except Exception as e:
            logger.error(f"DatabaseQuery initialization failed: {e}")
            raise

    def execute_query(self, query: str):
        try:
            schema = self.db_manager.get_schema()
            sql_prompt = ChatPromptTemplate.from_template(
                """
                You are a PostgreSQL expert. Write a single, executable SQL query to answer the query.
                Return ONLY the SQL query, no explanations or comments.
                If no relevant tables/columns are found, return an empty string.
                Schema: {schema}
                Query: {query}
                """
            )
            sql_chain = sql_prompt | self.llm | self.parser
            sql_query = sql_chain.invoke({"schema": schema, "query": query}).strip()
            if not sql_query:
                logger.error("No valid SQL query generated")
                return {"sql_query": "", "raw_response": "Error: No valid SQL query generated", "natural_language_response": "No valid SQL query could be generated."}

            results = self.db_manager.execute_query(sql_query)
            raw_response = str(results)

            nl_prompt = ChatPromptTemplate.from_template(
                """
                Convert the SQL query results into a concise natural language response (1-2 sentences).
                Query: {query}
                SQL Results: {results}
                """
            )
            nl_chain = nl_prompt | self.llm | self.parser
            natural_language_response = nl_chain.invoke({"query": query, "results": raw_response})

            logger.info(f"Database query executed: {query}, SQL: {sql_query}")
            return {
                "sql_query": sql_query,
                "raw_response": raw_response,
                "natural_language_response": natural_language_response
            }
        except Exception as e:
            logger.error(f"Database query failed for query '{query}': {e}")
            return {
                "sql_query": "",
                "raw_response": f"Error: Database query failed: {str(e)}",
                "natural_language_response": f"An error occurred while processing the query: {str(e)}"
            }