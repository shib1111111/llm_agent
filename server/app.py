from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import Optional, List
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
import os
import shutil
from database import DatabaseManager
from document_processor import DocumentProcessor
from llm_agent import QueryAgent
from config import CONFIG, logger

app = FastAPI(title="LLM Agent API")

# JWT Configuration
SECRET_KEY = "your-secret-key-please-change-this"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Database configuration
DB_URI = "postgresql+psycopg2://postgres:1234@localhost:5432/DataCoSupplyChain"
DOC_FOLDER = r"C:\Users\shib kumar saraf\Downloads\llm_agent\dataset\pdfs"

# Pydantic models
class User(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class QueryRequest(BaseModel):
    query: str

class DirectQueryRequest(BaseModel):
    query: str

# User database (for demo purposes, replace with proper database in production)
users_db = {}

# Authentication functions
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    if username not in users_db:
        raise credentials_exception
    return username

# Initialize components
db_manager = DatabaseManager(DB_URI)
doc_processor = DocumentProcessor(DOC_FOLDER)
vector_store = None

try:
    db_manager.connect()
    vector_store = doc_processor.process_documents()
    logger.info("Initial setup completed")
except Exception as e:
    logger.error(f"Initial setup failed: {e}")

# API Endpoints
@app.post("/signup")
async def signup(user: User):
    if user.username in users_db:
        raise HTTPException(status_code=400, detail="Username already registered")
    users_db[user.username] = {
        "username": user.username,
        "hashed_password": get_password_hash(user.password)
    }
    return {"message": "User created successfully"}

@app.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = users_db.get(form_data.username)
    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": form_data.username})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/db/connect")
async def check_db_connection(current_user: str = Depends(get_current_user)):
    try:
        schema = db_manager.get_schema()
        return {"status": "success", "message": "Database connected successfully", "schema": schema}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database connection failed: {str(e)}")

@app.post("/documents/upload")
async def upload_document(file: UploadFile = File(...), current_user: str = Depends(get_current_user)):
    try:
        # Save uploaded file
        file_path = os.path.join(DOC_FOLDER, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Process new document
        vector_store = doc_processor.process_documents()
        return {
            "status": "success",
            "message": f"Document {file.filename} uploaded and processed",
            "filename": file.filename
        }
    except Exception as e:
        logger.error(f"Document upload failed: {e}")
        raise HTTPException(status_code=500, detail=f"Document upload failed: {str(e)}")

@app.post("/query")
async def process_query(request: QueryRequest, current_user: str = Depends(get_current_user)):
    try:
        agent = QueryAgent(db_manager, vector_store)
        response = agent.execute_query(request.query)
        return {
            "status": "success",
            "query": request.query,
            "response": response
        }
    except Exception as e:
        logger.error(f"Query processing failed: {e}")
        raise HTTPException(status_code=500, detail=f"Query processing failed: {str(e)}")

@app.post("/db/query")
async def direct_db_query(request: DirectQueryRequest, current_user: str = Depends(get_current_user)):
    try:
        results = db_manager.execute_query(request.query)
        return {
            "status": "success",
            "query": request.query,
            "results": results
        }
    except Exception as e:
        logger.error(f"Direct DB query failed: {e}")
        raise HTTPException(status_code=500, detail=f"Direct DB query failed: {str(e)}")

@app.post("/documents/query")
async def direct_doc_query(request: DirectQueryRequest, current_user: str = Depends(get_current_user)):
    try:
        docs = vector_store.similarity_search(request.query, k=3)
        doc_content = "\n".join([doc.page_content for doc in docs])
        return {
            "status": "success",
            "query": request.query,
            "results": doc_content,
            "documents_found": len(docs)
        }
    except Exception as e:
        logger.error(f"Direct document query failed: {e}")
        raise HTTPException(status_code=500, detail=f"Direct document query failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8080)