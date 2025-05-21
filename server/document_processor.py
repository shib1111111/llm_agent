import os
import json
import hashlib
from filelock import FileLock
from PyPDF2 import PdfReader
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from config import logger, CONFIG

class DocumentProcessor:
    def __init__(self, doc_folder: str):
        self.doc_folder = doc_folder
        self.vector_store = None
        self.embeddings_model = None
        self.metadata_path = os.path.join(CONFIG["PROCESSED_DOCS_DIR"], "metadata.json")
        os.makedirs(CONFIG["PROCESSED_DOCS_DIR"], exist_ok=True)

    def initialize_embeddings(self):
        try:
            self.embeddings_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
            logger.info("Embeddings model initialized")
            print("Step: Embeddings model initialized")
        except Exception as e:
            logger.error(f"Error initializing embeddings: {e}")
            print(f"Error: Embeddings initialization failed: {e}")
            raise

    def compute_checksum(self, file_path):
        try:
            hash_sha256 = hashlib.sha256()
            with open(file_path, "rb") as f:
                while chunk := f.read(8192):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
        except Exception as e:
            logger.error(f"Error computing checksum for {file_path}: {e}")
            print(f"Error: Checksum computation failed for {file_path}: {e}")
            return None

    def load_metadata(self):
        lock_path = self.metadata_path + ".lock"
        try:
            with FileLock(lock_path):
                if not os.path.exists(self.metadata_path):
                    return {}
                with open(self.metadata_path, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Error loading metadata: {e}")
            print(f"Error: Metadata loading failed: {e}")
            return {}

    def save_metadata(self, metadata):
        lock_path = self.metadata_path + ".lock"
        try:
            with FileLock(lock_path):
                with open(self.metadata_path, "w", encoding="utf-8") as f:
                    json.dump(metadata, f, indent=4)
            logger.info("Metadata saved")
            print("Step: Metadata saved")
        except Exception as e:
            logger.error(f"Error saving metadata: {e}")
            print(f"Error: Metadata saving failed: {e}")
            raise

    def extract_text_from_pdf(self, file_path):
        try:
            with open(file_path, "rb") as file:
                pdf_reader = PdfReader(file)
                text = "".join(page.extract_text() or "" for page in pdf_reader.pages)
            logger.info(f"Text extracted from {file_path}")
            print(f"Step: Text extracted from {file_path}")
            return text
        except Exception as e:
            logger.error(f"Error extracting text from {file_path}: {e}")
            print(f"Error: Text extraction failed for {file_path}: {e}")
            return ""

    def split_text_into_chunks(self, text: str):
        try:
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
            chunks = text_splitter.split_text(text)
            logger.info("Text split into chunks")
            print("Step: Text split into chunks")
            return chunks
        except Exception as e:
            logger.error(f"Error splitting text: {e}")
            print(f"Error: Text splitting failed: {e}")
            return []

    def process_documents(self):
        self.initialize_embeddings()  # Load embeddings model first
        metadata = self.load_metadata()
        text_chunks = []
        metadatas = []
        new_files_processed = False

        print("Step: Checking for new documents to process...")
        for file_name in os.listdir(self.doc_folder):
            file_path = os.path.join(self.doc_folder, file_name)
            if os.path.splitext(file_name)[1].lower() != ".pdf":
                logger.info(f"Skipping non-PDF file: {file_path}")
                # print(f"Step: Skipping non-PDF file: {file_path}")
                continue

            checksum = self.compute_checksum(file_path)
            if not checksum or checksum in metadata:
                logger.info(f"Skipping already processed file: {file_path}")
                # print(f"Step: Skipping already processed file: {file_path}")
                continue

            text = self.extract_text_from_pdf(file_path)
            if not text:
                continue

            chunks = self.split_text_into_chunks(text)
            if not chunks:
                continue

            text_chunks.extend(chunks)
            metadatas.extend([{"file_name": file_name, "checksum": checksum} for _ in chunks])
            metadata[checksum] = {"original_name": file_name}
            new_files_processed = True

        if new_files_processed:
            print("Step: Processing new documents...")
            self.vector_store = FAISS.from_texts(
                texts=text_chunks,
                embedding=self.embeddings_model,
                metadatas=metadatas
            )
            index_path = os.path.join(CONFIG["PROCESSED_DOCS_DIR"], "faiss_index")
            self.vector_store.save_local(index_path)
            self.save_metadata(metadata)
            logger.info("New documents processed and vector store saved")
            print(f"Step: Vector store created with {len(text_chunks)} chunks")
        else:
            print("Step: No new documents to process")

        return self.load_vector_store()

    def load_vector_store(self):
        try:
            index_path = os.path.join(CONFIG["PROCESSED_DOCS_DIR"], "faiss_index")
            if os.path.exists(index_path):
                self.vector_store = FAISS.load_local(
                    index_path,
                    self.embeddings_model,
                    allow_dangerous_deserialization=True
                )
                logger.info("Vector store loaded")
                print(f"Step: Vector store loaded with {len(self.vector_store.docstore._dict)} documents")
            else:
                logger.info("No existing vector store found")
                print("Step: No existing vector store found")
            return self.vector_store
        except Exception as e:
            logger.error(f"Error loading vector store: {e}")
            print(f"Error: Vector store loading failed: {e}")
            raise
