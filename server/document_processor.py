import os
import json
import hashlib
from filelock import FileLock
from PyPDF2 import PdfReader
from langchain_community.vectorstores import FAISS
from llm_models import BedrockEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from config import logger, CONFIG

class DocumentProcessor:
    def __init__(self, doc_folder: str, role: str):
        try:
            self.doc_folder = os.path.join(doc_folder, role)
            self.role = role
            self.vector_store = None
            self.embeddings_model = None
            self.metadata_path = os.path.join(CONFIG["PROCESSED_DOCS_DIR"], f"metadata_{role}.json")
            self.index_path = os.path.join(CONFIG["PROCESSED_DOCS_DIR"], f"faiss_index_{role}")
            os.makedirs(CONFIG["PROCESSED_DOCS_DIR"], exist_ok=True)
            os.makedirs(self.doc_folder, exist_ok=True)
        except Exception as e:
            logger.error(f"Initialization failed for role {role}: {e}")
            raise

    def initialize_embeddings(self):
        try:
            self.embeddings_model = BedrockEmbeddings(api_key=CONFIG["ANTHROPIC_API_KEY"], model_id="amazon-embedding-v2")
            logger.info(f"Embeddings model initialized for role {self.role}")
        except Exception as e:
            logger.error(f"Error initializing embeddings for role {self.role}: {e}")
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
            logger.error(f"Error loading metadata for role {self.role}: {e}")
            return {}

    def save_metadata(self, metadata):
        lock_path = self.metadata_path + ".lock"
        try:
            with FileLock(lock_path):
                with open(self.metadata_path, "w", encoding="utf-8") as f:
                    json.dump(metadata, f, indent=4)
            logger.info(f"Metadata saved for role {self.role}")
        except Exception as e:
            logger.error(f"Error saving metadata for role {self.role}: {e}")
            raise

    def extract_text_from_pdf(self, file_path):
        try:
            with open(file_path, "rb") as file:
                pdf_reader = PdfReader(file)
                text = "".join(page.extract_text() or "" for page in pdf_reader.pages)
            logger.info(f"Text extracted from {file_path} for role {self.role}")
            return text
        except Exception as e:
            logger.error(f"Error extracting text from {file_path} for role {self.role}: {e}")
            return ""

    def split_text_into_chunks(self, text: str):
        try:
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
            chunks = text_splitter.split_text(text)
            logger.info(f"Text split into chunks for role {self.role}")
            return chunks
        except Exception as e:
            logger.error(f"Error splitting text for role {self.role}: {e}")
            return []

    def process_documents(self):
        try:
            self.initialize_embeddings()
            metadata = self.load_metadata()
            text_chunks = []
            metadatas = []
            new_files_processed = False

            for file_name in os.listdir(self.doc_folder):
                file_path = os.path.join(self.doc_folder, file_name)
                if os.path.splitext(file_name)[1].lower() != ".pdf":
                    logger.info(f"Skipping non-PDF file: {file_path} for role {self.role}")
                    continue

                checksum = self.compute_checksum(file_path)
                if not checksum or checksum in metadata:
                    logger.info(f"Skipping already processed file: {file_path} for role {self.role}")
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
                self.vector_store = FAISS.from_texts(
                    texts=text_chunks,
                    embedding=self.embeddings_model,
                    metadatas=metadatas
                )
                self.vector_store.save_local(self.index_path)
                self.save_metadata(metadata)
                logger.info(f"New documents processed and vector store saved for role {self.role}")
            else:
                logger.info(f"No new documents to process for role {self.role}")

            return self.load_vector_store()
        except Exception as e:
            logger.error(f"Document processing failed for role {self.role}: {e}")
            raise

    def load_vector_store(self):
        try:
            if os.path.exists(self.index_path):
                self.vector_store = FAISS.load_local(
                    self.index_path,
                    self.embeddings_model,
                    allow_dangerous_deserialization=True
                )
                logger.info(f"Vector store loaded for role {self.role}")
            else:
                logger.info(f"No existing vector store found for role {self.role}")
            return self.vector_store
        except Exception as e:
            logger.error(f"Error loading vector store for role {self.role}: {e}")
            raise