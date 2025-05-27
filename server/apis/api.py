from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session
from datetime import datetime
from zoneinfo import ZoneInfo
import os
import shutil
import uuid
from config import CONFIG, logger
from database import DatabaseManager
from doc_query import DocumentQuery
from document_processor import DocumentProcessor
from db_query import DatabaseQuery
from llm_agent import QueryAgent
from models import ChatHistory, Documents
from api_utils import create_standard_response, get_db, get_current_user
from schema import StandardResponse, QueryRequest, QueryResponse, DatabaseQueryResponse, DocumentUploadResponse

api_router = APIRouter(prefix="/api", tags=["api"])

@api_router.get("/connect", response_model=StandardResponse)
async def connect_db(current_user: dict = Depends(get_current_user)):
    """Connect to the database and return its schema (requires authentication)."""
    try:
        print(f'postgres db {CONFIG["DB_URI"]}')
        db_manager = DatabaseManager(CONFIG["DB_URI"])
        db_manager.connect()
        schema = db_manager.get_schema()
        logger.info(f"Database connected for user: {current_user['username']}")
        return create_standard_response(
            "success",
            "Successfully connected to the database.",
            {"schema": schema}
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Database connection failed for user {current_user['username']}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to connect to the database. Please try again later."
        )

@api_router.post("/documents/upload", response_model=StandardResponse)
async def upload_document(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload a document and process it for the user's role (requires authentication)."""
    try:
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only PDF files are allowed for upload."
            )
        role = current_user["role"]
        default_doc = db.query(Documents).filter(
            Documents.role == role,
            Documents.filename == file.filename,
            Documents.doc_type == "default"
        ).first()
        if not default_doc:
            logger.error(f"Unauthorized upload attempt: {file.filename} by user {current_user['username']} with role {role}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"You are not authorized to upload {file.filename} for role {role}."
            )
        role_folder = os.path.join(CONFIG["ROOT_DIR"], "dataset", "pdfs", role)
        os.makedirs(role_folder, exist_ok=True)
        file_path = os.path.join(role_folder, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        upload_record = Documents(
            user_id=current_user["id"],
            filename=file.filename,
            role=role,
            file_path=file_path,
            doc_type="uploaded",
            timestamp=datetime.now(ZoneInfo("Asia/Kolkata")),
        )
        db.add(upload_record)
        db.commit()
        doc_processor = DocumentProcessor(os.path.join(CONFIG["ROOT_DIR"], "dataset", "pdfs"), role)
        doc_processor.process_documents()
        logger.info(f"Document uploaded and processed: {file.filename} for role {role} by user {current_user['username']}")
        return create_standard_response(
            "success",
            f"Document {file.filename} uploaded and processed successfully for role {role}.",
            DocumentUploadResponse(filename=file.filename, role=role, timestamp=upload_record.timestamp).dict()
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Document upload failed for user {current_user['username']}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process document upload. Please try again later."
        )

@api_router.post("/query", response_model=StandardResponse)
async def agent_query(
    request: QueryRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Execute an agent query combining database and document data (requires authentication)."""
    try:
        if not request.query.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Query cannot be empty."
            )
        role = current_user["role"]
        doc_processor = DocumentProcessor(os.path.join(CONFIG["ROOT_DIR"], "dataset", "pdfs"), role)
        vector_store = doc_processor.process_documents()
        print(f'postgres db {CONFIG["DB_URI"]}')
        db_manager = DatabaseManager(CONFIG["DB_URI"])
        db_manager.connect()
        agent = QueryAgent(db_manager, vector_store)
        start_time = datetime.now(ZoneInfo("Asia/Kolkata"))
        response = agent.execute_query(request.query)
        query_processing_time = (datetime.now(ZoneInfo("Asia/Kolkata")) - start_time).total_seconds()
        response_id = str(uuid.uuid4())
        db.add(
            ChatHistory(
                user_id=current_user["id"],
                query=request.query,
                response=response,
                response_id=response_id,
                query_type="agent",
                query_processing_time=query_processing_time,
                chat_timestamp=datetime.now(ZoneInfo("Asia/Kolkata")),
            )
        )
        db.commit()
        logger.info(f"Agent query executed by user {current_user['username']}: {request.query}")
        return create_standard_response(
            "success",
            "Query executed successfully.",
            QueryResponse(query=request.query, response=response).dict()
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Agent query failed for user {current_user['username']}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process query. Please try again later."
        )

@api_router.post("/documents/query", response_model=StandardResponse)
async def doc_query(
    request: QueryRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Execute a query on documents for the user's role (requires authentication)."""
    try:
        if not request.query.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Query cannot be empty."
            )
        role = current_user["role"]
        doc_processor = DocumentProcessor(os.path.join(CONFIG["ROOT_DIR"], "dataset", "pdfs"), role)
        vector_store = doc_processor.process_documents()
        doc_query_handler = DocumentQuery(vector_store)
        start_time = datetime.now(ZoneInfo("Asia/Kolkata"))
        response = doc_query_handler.execute_query(request.query)
        query_processing_time = (datetime.now(ZoneInfo("Asia/Kolkata")) - start_time).total_seconds()
        response_id = str(uuid.uuid4())
        db.add(
            ChatHistory(
                user_id=current_user["id"],
                query=request.query,
                response=response,
                response_id=response_id,
                query_type="doc",
                query_processing_time=query_processing_time,
                chat_timestamp=datetime.now(ZoneInfo("Asia/Kolkata")),
            )
        )
        db.commit()
        logger.info(f"Document query executed by user {current_user['username']}: {request.query}")
        return create_standard_response(
            "success",
            "Document query executed successfully.",
            QueryResponse(query=request.query, response=response).dict()
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Document query failed for user {current_user['username']}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process document query. Please try again later."
        )

@api_router.post("/db/query", response_model=StandardResponse)
async def db_query(
    request: QueryRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Execute a database query (requires authentication)."""
    try:
        if not request.query.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Query cannot be empty."
            )
        db_manager = DatabaseManager(CONFIG["DB_URI"])
        db_manager.connect()
        db_query_handler = DatabaseQuery(db_manager)
        start_time = datetime.now(ZoneInfo("Asia/Kolkata"))
        result = db_query_handler.execute_query(request.query)
        query_processing_time = (datetime.now(ZoneInfo("Asia/Kolkata")) - start_time).total_seconds()
        response_id = str(uuid.uuid4())
        db.add(
            ChatHistory(
                user_id=current_user["id"],
                query=request.query,
                response=result["natural_language_response"],
                response_id=response_id,
                query_type="db",
                query_processing_time=query_processing_time,
                chat_timestamp=datetime.now(ZoneInfo("Asia/Kolkata")),
            )
        )
        db.commit()
        logger.info(f"Database query executed by user {current_user['username']}: {request.query}")
        return create_standard_response(
            "success",
            "Database query executed successfully.",
            DatabaseQueryResponse(
                query=request.query,
                sql_query=result["sql_query"],
                raw_response=result["raw_response"],
                natural_language_response=result["natural_language_response"],
            ).dict()
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Database query failed for user {current_user['username']}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process database query. Please try again later."
        )