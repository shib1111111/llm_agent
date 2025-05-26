from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from llm_models import BedrockLanguageModel
from config import CONFIG, logger

class DocumentQuery:
    def __init__(self, vector_store):
        try:
            self.vector_store = vector_store
            self.llm = BedrockLanguageModel(api_key=CONFIG["ANTHROPIC_API_KEY"], model_id="claude-3.5-sonnet")
            self.parser = StrOutputParser()
            logger.info("DocumentQuery initialized")
        except Exception as e:
            logger.error(f"DocumentQuery initialization failed: {e}")
            raise

    def execute_query(self, query: str):
        try:
            docs = self.vector_store.similarity_search(query, k=3)
            doc_content = "\n".join([doc.page_content for doc in docs])
            prompt = ChatPromptTemplate.from_template(
                """
                Summarize information from the documents to answer the query.
                Provide a concise summary (2-3 sentences).
                If no relevant information is found, return: "No relevant document information found."
                Query: {query}
                Documents: {documents}
                """
            )
            chain = prompt | self.llm | self.parser
            response = chain.invoke({"query": query, "documents": doc_content})
            logger.info(f"Document query executed: {query}")
            return response
        except Exception as e:
            logger.error(f"Document query failed for query '{query}': {e}")
            return f"Error: Document query failed: {str(e)}"