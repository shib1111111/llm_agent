import json
import os
import sys
import uuid
import hashlib
import logging
from filelock import FileLock
from typing import TypedDict, Optional, Dict, List
from langgraph.graph import StateGraph, END
from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate
from langchain_community.vectorstores import FAISS
from langchain_community.utilities import SQLDatabase
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain.text_splitter import RecursiveCharacterTextSplitter
from dotenv import load_dotenv
from PyPDF2 import PdfReader
from contextlib import contextmanager
import warnings

# Suppress warnings
@contextmanager
def suppress_warnings():
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        yield

# Configure logging to only show errors and output to console
logging.basicConfig(
    level=logging.ERROR,  # Suppress INFO logs (e.g., vector store creation)
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# Add onnxruntime to PATH (Windows-specific)
try:
    import onnxruntime
    onnx_path = os.path.dirname(onnxruntime.__file__) + "\\capi"
    os.environ["PATH"] = onnx_path + os.pathsep + os.environ["PATH"]
except ImportError:
    logger.error("Failed to import onnxruntime; using HuggingFaceEmbeddings as fallback")

# Load environment variables
try:
    with suppress_warnings():
        load_dotenv()
except Exception as e:
    logger.error(f"Error loading environment variables: {e}")
    sys.exit(1)

# State definition for LangGraph
class AgentState(TypedDict):
    query: str
    db_uri: str
    doc_folder: str
    intent: Optional[str]  # document, data, hybrid
    document_results: Optional[str]
    sql_query: Optional[str]
    db_results: Optional[List[Dict]]
    final_response: Optional[str]
    context: List[str]  # Short-term memory
    vector_store: Optional[FAISS]
    db: Optional[SQLDatabase]

# Initialize Groq LLM
try:
    llm = ChatGroq(model="llama-3.3-70b-versatile", api_key=os.getenv("GROQ_API_KEY"))
except Exception as e:
    logger.error(f"Error initializing LLM: {e}")
    sys.exit(1)

# Directory for storing processed document metadata
PROCESSED_DOCS_DIR = "processed_doc"
try:
    with suppress_warnings():
        os.makedirs(PROCESSED_DOCS_DIR, exist_ok=True)
except Exception as e:
    logger.error(f"Error creating directory {PROCESSED_DOCS_DIR}: {e}")

# Prompt templates
intent_prompt = ChatPromptTemplate.from_template(
    "Given the query: '{query}' and database schema: {schema}, classify the intent as 'document', 'data', or 'hybrid'. Provide a brief explanation."
)

doc_prompt = ChatPromptTemplate.from_template(
    "Given the query: '{query}' and the following documents: {documents}, summarize the relevant information in a concise manner."
)

sql_prompt = ChatPromptTemplate.from_template(
    """
    You are a data analyst. Based on the PostgreSQL schema below, write a secure and efficient SQL query for the user's question. Consider the conversation history.
    <SCHEMA>{schema}</SCHEMA>
    Conversation History: {chat_history}
    Question: {question}
    SQL Query:
    """
)

response_prompt = ChatPromptTemplate.from_template(
    """
    You are a data analyst. Based on the schema, question, SQL query, SQL response, and document results, write a natural language response.
    <SCHEMA>{schema}</SCHEMA>
    Conversation History: {chat_history}
    User question: {question}
    SQL Query: <SQL>{query}</SQL>
    SQL Response: {sql_response}
    Document Results: {doc_results}
    """
)

# Cache embeddings model globally
embeddings_model = None

# Compute SHA-256 checksum of a file
def compute_checksum(file):
    try:
        hash_sha256 = hashlib.sha256()
        while chunk := file.read(8192):
            hash_sha256.update(chunk)
        file.seek(0)
        return hash_sha256.hexdigest()
    except Exception as e:
        logger.error(f"Error computing checksum: {e}")
        return None

# Load metadata from JSON
def load_metadata():
    metadata_path = os.path.join(PROCESSED_DOCS_DIR, "metadata.json")
    lock_path = metadata_path + ".lock"
    try:
        with FileLock(lock_path):
            if not os.path.exists(metadata_path):
                return {}
            if os.path.getsize(metadata_path) == 0:
                os.remove(metadata_path)
                return {}
            with open(metadata_path, "r", encoding="utf-8") as f:
                metadata = json.load(f)
                if not isinstance(metadata, dict):
                    os.remove(metadata_path)
                    return {}
                return metadata
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding JSON in {metadata_path}: {e}")
        os.remove(metadata_path)
        return {}
    except Exception as e:
        logger.error(f"Error loading metadata from {metadata_path}: {e}")
        return {}

# Save metadata to JSON
def save_metadata(metadata):
    metadata_path = os.path.join(PROCESSED_DOCS_DIR, "metadata.json")
    lock_path = metadata_path + ".lock"
    try:
        with FileLock(lock_path):
            os.makedirs(PROCESSED_DOCS_DIR, exist_ok=True)
            with open(metadata_path, "w", encoding="utf-8") as f:
                json.dump(metadata, f, indent=4, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Error saving metadata to {metadata_path}: {e}")
        raise

# Extract text from PDF
def extract_text_from_pdf(file):
    try:
        pdf_reader = PdfReader(file)
        text = ""
        for page in pdf_reader.pages:
            page_text = page.extract_text() or ""
            text += page_text
        return text
    except Exception as e:
        logger.error(f"Error extracting text from PDF: {e}")
        return ""

# Split text into chunks
def split_text_into_chunks(text, chunk_size=1000, chunk_overlap=100):
    try:
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        return text_splitter.split_text(text)
    except Exception as e:
        logger.error(f"Error splitting text: {e}")
        return []

# Create and save FAISS vector store
def create_vector_store_from_chunks(text_chunks, checksum):
    global embeddings_model
    try:
        if embeddings_model is None:
            try:
                from fastembed import FastEmbedEmbeddings
                embeddings_model = FastEmbedEmbeddings()
            except ImportError:
                embeddings_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        
        vector_store = FAISS.from_texts(
            texts=text_chunks,
            embedding=embeddings_model,
            metadatas=[{"checksum": checksum} for _ in text_chunks]
        )
        index_path = os.path.join(PROCESSED_DOCS_DIR, f"faiss_index_{checksum}")
        vector_store.save_local(index_path)
        return index_path
    except Exception as e:
        logger.error(f"Error creating vector store: {e}")
        if not isinstance(embeddings_model, HuggingFaceEmbeddings):
            try:
                embeddings_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
                vector_store = FAISS.from_texts(
                    texts=text_chunks,
                    embedding=embeddings_model,
                    metadatas=[{"checksum": checksum} for _ in text_chunks]
                )
                index_path = os.path.join(PROCESSED_DOCS_DIR, f"faiss_index_{checksum}_fallback")
                vector_store.save_local(index_path)
                return index_path
            except Exception as fallback_e:
                logger.error(f"Error creating fallback vector store: {fallback_e}")
                return None
        return None

# Process documents in folder
def process_documents(doc_folder):
    metadata = load_metadata()
    batch_id = str(uuid.uuid4())
    batch_metadata = {}
    vector_stores = []

    try:
        for file_name in os.listdir(doc_folder):
            file_path = os.path.join(doc_folder, file_name)
            file_extension = os.path.splitext(file_name)[1].lower()

            if file_extension not in [".pdf", ".txt"]:
                logger.error(f"Skipping unsupported file: {file_path}")
                continue

            with open(file_path, "rb") as file:
                checksum = compute_checksum(file)
                if not checksum:
                    logger.error(f"Skipping file due to checksum error: {file_path}")
                    continue

                existing_metadata = None
                for existing_batch_id, files in metadata.items():
                    if checksum in files:
                        existing_metadata = files[checksum]
                        break

                if existing_metadata:
                    batch_metadata[checksum] = {
                        "original_name": file_name,
                        "index_path": existing_metadata["index_path"]
                    }
                    try:
                        global embeddings_model
                        if embeddings_model is None:
                            try:
                                from fastembed import FastEmbedEmbeddings
                                embeddings_model = FastEmbedEmbeddings()
                            except ImportError:
                                embeddings_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
                        vector_stores.append(FAISS.load_local(
                            existing_metadata["index_path"],
                            embeddings_model,
                            allow_dangerous_deserialization=True
                        ))
                    except Exception as e:
                        logger.error(f"Error loading vector store for {file_path}: {e}")
                        continue
                    continue

                file.seek(0)
                if file_extension == ".pdf":
                    raw_text = extract_text_from_pdf(file)
                else:  # .txt
                    raw_text = file.read().decode("utf-8", errors="ignore")

                text_chunks = split_text_into_chunks(raw_text)
                if not text_chunks:
                    logger.error(f"No valid chunks for {file_path}")
                    continue

                index_path = create_vector_store_from_chunks(text_chunks, checksum)
                if index_path:
                    batch_metadata[checksum] = {
                        "original_name": file_name,
                        "index_path": index_path
                    }
                    try:
                        vector_stores.append(FAISS.load_local(
                            index_path,
                            embeddings_model,
                            allow_dangerous_deserialization=True
                        ))
                    except Exception as e:
                        logger.error(f"Error loading vector store for {file_path}: {e}")
                        continue

        if batch_metadata:
            save_metadata({**metadata, batch_id: batch_metadata})

        if len(vector_stores) > 1:
            merged_store = vector_stores[0]
            for store in vector_stores[1:]:
                try:
                    merged_store.merge_from(store)
                except Exception as e:
                    logger.error(f"Error merging vector stores: {e}")
            return merged_store
        return vector_stores[0] if vector_stores else None

    except Exception as e:
        logger.error(f"Error processing documents: {e}")
        return None

# Node: Initialize database and documents
def init_db_and_docs(state: AgentState) -> AgentState:
    print("\nStep 1: Connecting to database and processing documents...")
    try:
        state["db"] = SQLDatabase.from_uri(state["db_uri"])
        print("Database connection established.")
    except Exception as e:
        state["final_response"] = f"Error connecting to database: {str(e)}"
        logger.error(f"Database connection error: {e}")
        print(f"Error: Failed to connect to database: {str(e)}")
        return state

    vector_store = process_documents(state["doc_folder"])
    if vector_store:
        state["vector_store"] = vector_store
        print("Documents processed successfully.")
    else:
        state["final_response"] = "Error: No valid documents found in the folder."
        logger.error("No valid documents found in the folder.")
        print("Error: No valid documents found in the folder.")
    return state

# Node: Intent determination
def determine_intent(state: AgentState) -> AgentState:
    if state["final_response"]:
        return state
    print("\nStep 2: Determining query intent...")
    try:
        schema = state["db"].get_table_info()
        prompt = intent_prompt.format_messages(query=state["query"], schema=schema)
        intent_response = llm.invoke(prompt)
        state["intent"] = intent_response.content.split("\n")[0]
        state["context"].append(f"Query: {state['query']}, Intent: {state['intent']}")
        print(f"Intent classified as: {state['intent']}")
        print(f"Context updated: {state['context']}")
    except Exception as e:
        state["final_response"] = f"Error determining intent: {str(e)}"
        logger.error(f"Error determining intent: {e}")
        print(f"Error: Failed to determine intent: {str(e)}")
    return state

# Node: Document retrieval
def retrieve_documents(state: AgentState) -> AgentState:
    if state["final_response"] or state["intent"] not in ["document", "hybrid"]:
        return state
    print("\nStep 3: Retrieving relevant documents...")
    try:
        docs = state["vector_store"].similarity_search(state["query"], k=3)
        doc_content = "\n".join([doc.page_content for doc in docs])
        prompt = doc_prompt.format_messages(query=state["query"], documents=doc_content)
        state["document_results"] = llm.invoke(prompt).content
        print("Documents retrieved successfully.")
    except Exception as e:
        state["final_response"] = f"Error retrieving documents: {str(e)}"
        logger.error(f"Error retrieving documents: {e}")
        print(f"Error: Failed to retrieve documents: {str(e)}")
    return state

# Node: SQL query generation and execution
def generate_sql_chain(state: AgentState) -> AgentState:
    if state["final_response"] or state["intent"] not in ["data", "hybrid"]:
        return state
    print("\nStep 4: Generating and executing SQL query...")
    try:
        schema = state["db"].get_table_info()
        prompt = sql_prompt.format_messages(
            schema=schema,
            chat_history="\n".join(state["context"]),
            question=state["query"]
        )
        sql_query = llm.invoke(prompt).content
        state["sql_query"] = sql_query
        results = state["db"].run(sql_query)
        state["db_results"] = eval(results) if results else []
        print(f"SQL Query: {sql_query}")
        print(f"Database results: {state['db_results']}")
    except Exception as e:
        state["final_response"] = f"Error executing query: {str(e)}"
        logger.error(f"Error executing query: {e}")
        print(f"Error: Failed to execute SQL query: {str(e)}")
    return state

# Node: Response generation
def generate_response(state: AgentState) -> AgentState:
    if state["final_response"]:
        return state
    print("\nStep 5: Generating final response...")
    try:
        schema = state["db"].get_table_info()
        prompt = response_prompt.format_messages(
            schema=schema,
            chat_history="\n".join(state["context"]),
            question=state["query"],
            query=state["sql_query"] or "None",
            sql_response=str(state["db_results"]),
            doc_results=state["document_results"] or "None"
        )
        state["final_response"] = llm.invoke(prompt).content
        print("Final response generated successfully.")
    except Exception as e:
        state["final_response"] = f"Error generating response: {str(e)}"
        logger.error(f"Error generating response: {e}")
        print(f"Error: Failed to generate response: {str(e)}")
    return state

# Define the workflow
workflow = StateGraph(AgentState)

# Add nodes
workflow.add_node("init_db_and_docs", init_db_and_docs)
workflow.add_node("determine_intent", determine_intent)
workflow.add_node("retrieve_documents", retrieve_documents)
workflow.add_node("generate_sql_chain", generate_sql_chain)
workflow.add_node("generate_response", generate_response)

# Define edges
workflow.set_entry_point("init_db_and_docs")
workflow.add_edge("init_db_and_docs", "determine_intent")
workflow.add_edge("determine_intent", "retrieve_documents")
workflow.add_edge("retrieve_documents", "generate_sql_chain")
workflow.add_edge("generate_sql_chain", "generate_response")
workflow.add_edge("generate_response", END)

# Compile the graph
try:
    app = workflow.compile()
except Exception as e:
    logger.error(f"Error compiling workflow: {e}")
    print(f"Error: Failed to compile workflow: {str(e)}")
    sys.exit(1)

# Execute workflow
def run_agent(query: str, db_uri: str, doc_folder: str) -> str:
    print(f"\n=== Starting Agent Execution ===")
    print(f"Query: '{query}'")
    print(f"Database URI: {db_uri}")
    print(f"Document folder: {doc_folder}")
    print("Initializing agent state...")

    state = AgentState(
        query=query,
        db_uri=db_uri,
        doc_folder=doc_folder,
        intent=None,
        document_results=None,
        sql_query=None,
        db_results=None,
        final_response=None,
        context=[],
        vector_store=None,
        db=None
    )

    with suppress_warnings():
        try:
            result = app.invoke(state)
            print("\n=== Agent Execution Completed ===")
            return result["final_response"]
        except Exception as e:
            logger.error(f"Error running agent: {e}")
            print(f"\nError: Agent execution failed: {str(e)}")
            return f"Error: {str(e)}"

# Example usage
if __name__ == "__main__":
    db_uri = "postgresql+psycopg2://postgres:1234@localhost:5432/DataCoSupplyChain"
    doc_folder = r"C:\Users\shib kumar saraf\Downloads\llm_agent\dataset\pdfs"
    query = "Which inventory items qualify as no-movers according to our policy, and how many do we have?"
    response = run_agent(query, db_uri, doc_folder)
    print(f"\nFinal Answer: {response}")