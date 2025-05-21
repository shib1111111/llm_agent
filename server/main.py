from database import DatabaseManager
from document_processor import DocumentProcessor
from llm_agent import QueryAgent
from config import logger

def setup_and_run_agent(query: str, db_uri: str, doc_folder: str):
    print("\n=== Setting Up Agent ===")
    
    # Step 1: Check database connection
    print("Step: Checking DB...")
    try:
        db_manager = DatabaseManager(db_uri)
        db_manager.connect()
    except Exception as e:
        logger.error(f"DB connection failed: {e}")
        print(f"Error: DB connection failed")
        return f"Error: Database connection failed: {str(e)}"

    # Step 2: Initialize document processor
    print("Step: Initializing documents...")
    try:
        doc_processor = DocumentProcessor(doc_folder)
        vector_store = doc_processor.process_documents()
        if not vector_store:
            logger.error("No documents found")
            print("Error: No documents found")
            return "Error: No documents found or processed"
    except Exception as e:
        logger.error(f"Document processor failed: {e}")
        print(f"Error: Document processor failed")
        return f"Error: Document processor failed: {str(e)}"

    # Step 3: Run agent
    print("Step: Running agent...")
    try:
        agent = QueryAgent(db_manager, vector_store)
        response = agent.execute_query(query)
        return response
    except Exception as e:
        logger.error(f"Agent failed: {e}")
        print(f"Error: Agent failed")
        return f"Error: Agent failed: {str(e)}"

if __name__ == "__main__":
    db_uri = "postgresql+psycopg2://postgres:1234@localhost:5432/DataCoSupplyChain"
    doc_folder = r"C:\Users\shib kumar saraf\Downloads\llm_agent\dataset\pdfs"
    query = "What is the average benefit per transaction?"

    response = setup_and_run_agent(query, db_uri, doc_folder)