# LangGraph Agent for Document and Database Querying

This project implements a LangGraph-based agent that processes user queries by combining document retrieval (from PDFs or text files) and SQL database querying. The agent uses a large language model (LLM) from Groq, FAISS for vector search, and PostgreSQL for data storage. It classifies query intent, retrieves relevant document snippets, generates and executes SQL queries, and produces a natural language response.

## Features
- **Intent Classification**: Determines if the query requires document retrieval, database querying, or both (hybrid).
- **Document Processing**: Extracts text from PDFs or text files, creates a FAISS vector store, and retrieves relevant snippets.
- **SQL Query Generation**: Uses the LLM to generate secure SQL queries based on the database schema and executes them.
- **Natural Language Response**: Combines document and database results into a concise, user-friendly response.
- **Error Handling**: Provides clear error messages for database connection issues, document processing failures, or other errors.
- **Clean Output**: Suppresses warnings and non-critical logs for a user-friendly experience.

## Prerequisites
- **Python**: Version 3.8 or higher.
- **PostgreSQL**: A running PostgreSQL database with the required schema.
- **Groq API Key**: Obtain from [xAI](https://x.ai/api).
- **Document Folder**: A directory containing `.pdf` or `.txt` files to process.
- **Dependencies**:
  ```bash
  pip install langchain langchain-groq langchain-community filelock PyPDF2 python-dotenv psycopg2-binary
  ```
  Optional (for faster embeddings):
  ```bash
  pip install onnxruntime fastembed
  ```

## Setup
1. **Clone the Repository** (if applicable):
   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```

2. **Set Up Environment Variables**:
   Create a `.env` file in the project root with your Groq API key:
   ```
   GROQ_API_KEY=your-api-key-here
   ```

3. **Configure PostgreSQL**:
   - Ensure a PostgreSQL database is running at `postgresql+psycopg2://postgres:1234@localhost:5432/DataCoSupplyChain` (modify the URI in `agent.py` if different).
   - Set up the database schema (e.g., tables for inventory data).

4. **Prepare Documents**:
   - Place `.pdf` or `.txt` files in the document folder (default: `C:\Users\shib kumar saraf\Downloads\llm_agent\dataset\pdfs`).
   - Update the `doc_folder` path in `agent.py` if needed.

5. **Install Dependencies**:
   Run the pip commands listed in the Prerequisites section.

## Usage
1. **Run the Script**:
   Execute the agent with the default query:
   ```bash
   python agent.py
   ```
   The default query is:
   ```
   Which inventory items qualify as no-movers according to our policy, and how many do we have?
   ```

2. **Custom Queries**:
   Modify the `query`, `db_uri`, and `doc_folder` in the `if __name__ == "__main__":` block of `agent.py`:
   ```python
   db_uri = "postgresql+psycopg2://<user>:<password>@<host>:<port>/<database>"
   doc_folder = "<path-to-your-document-folder>"
   query = "<your-custom-query>"
   response = run_agent(query, db_uri, doc_folder)
   print(f"\nFinal Answer: {response}")
   ```

3. **Expected Output**:
   The script prints the progress of each step:
   ```
   === Starting Agent Execution ===
   Query: 'Which inventory items qualify as no-movers according to our policy, and how many do we have?'
   Database URI: postgresql+psycopg2://postgres:1234@localhost:5432/DataCoSupplyChain
   Document folder: C:\Users\shib kumar saraf\Downloads\llm_agent\dataset\pdfs
   Initializing agent state...

   Step 1: Connecting to database and processing documents...
   Database connection established.
   Documents processed successfully.

   Step 2: Determining query intent...
   Intent classified as: hybrid
   Context updated: ["Query: Which inventory items qualify as no-movers according to our policy, and how many do we have?, Intent: hybrid"]

   Step 3: Retrieving relevant documents...
   Documents retrieved successfully.

   Step 4: Generating and executing SQL query...
   SQL Query: SELECT item_id, name FROM inventory WHERE sales = 0 AND last_sold < '2024-11-20';
   Database results: [{'item_id': 101, 'name': 'Widget A'}, {'item_id': 102, 'name': 'Widget B'}]

   Step 5: Generating final response...
   Final response generated successfully.

   === Agent Execution Completed ===

   Final Answer: According to the policy, no-movers are items with zero sales in the past 6 months. The database shows 2 no-movers: Widget A (ID 101) and Widget B (ID 102).
   ```

## Project Structure
- `agent.py`: Main script containing the LangGraph workflow and agent logic.
- `processed_doc/`: Directory for storing FAISS vector stores and metadata (`metadata.json`).
- `.env`: Environment file for storing the Groq API key.

## Workflow Overview
The agent processes queries through the following steps:
1. **Initialize Database and Documents**:
   - Connects to the PostgreSQL database.
   - Processes documents in the specified folder into a FAISS vector store.
2. **Determine Intent**:
   - Uses the LLM to classify the query as `document`, `data`, or `hybrid`.
3. **Retrieve Documents**:
   - Searches the vector store for relevant snippets (for `document` or `hybrid` intents).
4. **Generate and Execute SQL Query**:
   - Generates an SQL query using the LLM and executes it (for `data` or `hybrid` intents).
5. **Generate Response**:
   - Combines document and database results into a natural language response.

## Troubleshooting
- **Database Connection Error**:
  - Verify the `db_uri` in `agent.py`.
  - Ensure the PostgreSQL server is running and accessible.
  - Check the database credentials and schema.
- **No Documents Found**:
  - Confirm the `doc_folder` path exists and contains `.pdf` or `.txt` files.
  - Ensure files are not empty or corrupted.
- **API Key Error**:
  - Validate the `GROQ_API_KEY` in the `.env` file.
  - Check your Groq API subscription at [x.ai/api](https://x.ai/api).
- **Performance Issues**:
  - For large document folders, ensure sufficient memory and CPU resources.
  - Consider reducing the `chunk_size` in `split_text_into_chunks` for faster processing.
- **Warnings or Logs**:
  - The script suppresses warnings and non-critical logs for a clean output.
  - Check `agent.log` for error details if issues persist.

## Notes
- **Dependencies**: If `onnxruntime` or `fastembed` are unavailable, the script falls back to `HuggingFaceEmbeddings`.
- **Logging**: Only errors are logged to the console, suppressing informational logs (e.g., vector store creation).
- **Customization**: Modify the prompt templates in `agent.py` to adjust the LLM’s behavior.
- **Scalability**: For large datasets, consider optimizing FAISS indexing or using a more powerful machine.

## License
This project is unlicensed and provided as-is for educational purposes. Ensure compliance with the terms of use for Groq, LangChain, and other dependencies.

## Contact
For issues or contributions, please contact the project maintainer or open an issue on the repository (if applicable).