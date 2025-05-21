from langchain_community.utilities import SQLDatabase
from config import logger

class DatabaseManager:
    def __init__(self, db_uri: str):
        self.db_uri = db_uri
        self.db = None

    def connect(self):
        try:
            self.db = SQLDatabase.from_uri(self.db_uri)
            logger.info("Database connected")
            print("Step: Database connected")
            return self.db
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            print(f"Error: Database connection failed: {e}")
            raise

    def get_schema(self):
        if not self.db:
            raise ValueError("Database not connected")
        try:
            schema = self.db.get_table_info()
            logger.info("Database schema retrieved")
            print("Step: Database schema retrieved")
            return schema
        except Exception as e:
            logger.error(f"Error retrieving schema: {e}")
            print(f"Error: Schema retrieval failed: {e}")
            raise

    def execute_query(self, query: str):
        if not self.db:
            raise ValueError("Database not connected")
        try:
            results = self.db.run(query)
            logger.info(f"SQL query executed: {query}")
            print(f"Step: SQL query executed: {query}")
            return eval(results) if results else []
        except Exception as e:
            logger.error(f"Error executing query: {e}")
            print(f"Error: Query execution failed: {e}")
            raise