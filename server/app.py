from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
import os
import shutil
from sqlalchemy.orm import Session
from database import DatabaseManager
from document_processor import DocumentProcessor
from llm_agent import QueryAgent
from doc_query import DocumentQuery
from db_query import DatabaseQuery
from config import CONFIG, logger
from models import get_db_session, User, Session as UserSession, ChatHistory, LoginActivity, DocumentUpload, DefaultDoc

app = FastAPI(title="SCM Chatbot API")

SECRET_KEY = "your-secret-key-please-change-this"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

try:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
except Exception as e:
    logger.error(f"Failed to initialize password context: {e}")
    raise RuntimeError("Password context initialization failed")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

DB_URI = "postgresql+psycopg2://postgres:1234@localhost:5432/DataCoSupplyChain"
DOC_FOLDER = r"C:\Users\shib kumar saraf\Documents\llm_agent\dataset\pdfs"

ROLE_PDFS = {
    "admin": [
        "Anti-Counterfeit and Product Authenticity Policy.pdf",
        "Circular Economy.pdf",
        "COC.pdf",
        "Communication and Crisis Management Policy for DataCo Global.pdf",
        "Continuous Improvement.pdf",
        "Cost Reduction.pdf",
        "Data Security.pdf",
        "DataCo Global Capacity Planning Policy.pdf",
        "Dataco Global Change Management Policy for Supply Chain Processes.pdf",
        "DataCo Global Contract Management and Negotiation Policy.pdf",
        "Dataco Global Order Management Policy.pdf",
        "Dataco Global Transportation and Logistics Policy.pdf",
        "DataCo Global Warehouse and Storage Policy.pdf",
        "Dataco Global_ Demand Forecasting and Planning Policy.pdf",
        "Diversity and Inclusion in Supplier Base Policy for DataCo Global.pdf",
        "Environmental Sustainability.pdf",
        "Global Business Continuity.pdf",
        "Global Returns.pdf",
        "Health Safety and Environment (HSE) Policy for Supply Chain Management.pdf",
        "Inventory.pdf",
        "IOT.pdf",
        "KPI.pdf",
        "Labor Standards.pdf",
        "Obsolete Inventory Handling Policy for Dataco Global.pdf",
        "QA.pdf",
        "Risk Management.pdf",
        "Sourcing and Procurement Policy for DataCo Global.pdf",
        "SRM.pdf",
        "Supplier Selection.pdf",
        "Trade Compliance.pdf"
    ],
    "planning": [
        "Inventory.pdf",
        "Dataco Global Transportation and Logistics Policy.pdf",
        "Dataco Global_ Demand Forecasting and Planning Policy.pdf",
        "DataCo Global Capacity Planning Policy.pdf",
        "Continuous Improvement.pdf",
        "Obsolete Inventory Handling Policy for Dataco Global.pdf"
    ],
    "finance": [
        "Cost Reduction.pdf",
        "DataCo Global Contract Management and Negotiation Policy.pdf",
        "Sourcing and Procurement Policy for DataCo Global.pdf",
        "Risk Management.pdf"
    ],
    "operations": [
        "DataCo Global Warehouse and Storage Policy.pdf",
        "QA.pdf",
        "SRM.pdf",
        "Supplier Selection.pdf",
        "Health Safety and Environment (HSE) Policy for Supply Chain Management.pdf",
        "Global Returns.pdf"
    ]
}

class UserModel(BaseModel):
    username: str
    password: str
    role: str

class Token(BaseModel):
    access_token: str
    token_type: str

class QueryRequest(BaseModel):
    query: str

def get_db():
    try:
        db = get_db_session()
        yield db
    except Exception as e:
        logger.error(f"Failed to create database session: {e}")
        raise HTTPException(status_code=500, detail="Database session creation failed")
    finally:
        try:
            db.close()
        except Exception as e:
            logger.error(f"Failed to close database session: {e}")

def verify_password(plain_password, hashed_password):
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception as e:
        logger.error(f"Password verification failed: {e}")
        return False

def get_password_hash(password):
    try:
        return pwd_context.hash(password)
    except Exception as e:
        logger.error(f"Password hashing failed: {e}")
        raise HTTPException(status_code=500, detail="Password hashing failed")

def create_access_token(data: dict):
    try:
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt, expire
    except Exception as e:
        logger.error(f"Token creation failed: {e}")
        raise HTTPException(status_code=500, detail="Token creation failed")

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            logger.error("Invalid token: No username in payload")
            raise credentials_exception
    except JWTError as e:
        logger.error(f"Token decoding failed: {e}")
        raise credentials_exception
    try:
        user = db.query(User).filter(User.username == username).first()
        if not user:
            logger.error(f"User not found: {username}")
            raise credentials_exception
        session = db.query(UserSession).filter(UserSession.username == username, UserSession.token == token).first()
        if not session or session.expires_at < datetime.utcnow():
            logger.error(f"Invalid or expired session for user: {username}")
            raise credentials_exception
        return {"username": user.username, "role": user.role}
    except Exception as e:
        logger.error(f"User authentication failed: {e}")
        raise credentials_exception

@app.on_event("startup")
async def startup_event():
    try:
        db = get_db_session()
        for role, pdfs in ROLE_PDFS.items():
            try:
                for pdf in pdfs:
                    db.merge(DefaultDoc(role=role, filename=pdf))
                db.commit()
                doc_processor = DocumentProcessor(DOC_FOLDER, role)
                doc_processor.process_documents()
            except Exception as e:
                logger.error(f"Failed to process role {role}: {e}")
                raise
        logger.info("Startup: Processed all existing documents for all roles")
    except Exception as e:
        logger.error(f"Startup error: {e}")
        raise
    finally:
        try:
            db.close()
        except Exception as e:
            logger.error(f"Failed to close database session: {e}")

@app.post("/signup")
async def signup(user: UserModel, db: Session = Depends(get_db)):
    try:
        if user.role not in CONFIG["ROLES"]:
            logger.error(f"Invalid role: {user.role}")
            raise HTTPException(status_code=400, detail="Invalid role")
        existing_user = db.query(User).filter(User.username == user.username).first()
        if existing_user:
            logger.error(f"Username already registered: {user.username}")
            raise HTTPException(status_code=400, detail="Username already registered")
        hashed_password = get_password_hash(user.password)
        db_user = User(username=user.username, hashed_password=hashed_password, role=user.role)
        db.add(db_user)
        db.commit()
        logger.info(f"User created: {user.username}, role: {user.role}")
        return {"message": "User created successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Signup failed for user {user.username}: {e}")
        raise HTTPException(status_code=500, detail="Signup failed")

@app.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    try:
        user = db.query(User).filter(User.username == form_data.username).first()
        if not user or not verify_password(form_data.password, user.hashed_password):
            logger.error(f"Login failed for username: {form_data.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        session_id = os.urandom(16).hex()
        access_token, expires_at = create_access_token({"sub": user.username})
        db_session = UserSession(
            session_id=session_id,
            username=user.username,
            token=access_token,
            created_at=datetime.utcnow(),
            expires_at=expires_at
        )
        db.add(db_session)
        db.add(LoginActivity(username=user.username, action="login", timestamp=datetime.utcnow()))
        db.commit()
        logger.info(f"User logged in: {user.username}")
        return {"access_token": access_token, "token_type": "bearer"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login failed for username {form_data.username}: {e}")
        raise HTTPException(status_code=500, detail="Login failed")

@app.post("/logout")
async def logout(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        db.query(UserSession).filter(UserSession.username == current_user["username"]).delete()
        db.add(LoginActivity(username=current_user["username"], action="logout", timestamp=datetime.utcnow()))
        db.commit()
        logger.info(f"User logged out: {current_user['username']}")
        return {"message": "Logged out successfully"}
    except Exception as e:
        logger.error(f"Logout failed for user {current_user['username']}: {e}")
        raise HTTPException(status_code=500, detail="Logout failed")

@app.get("/db/connect")
async def connect_db(current_user: dict = Depends(get_current_user)):
    try:
        db_manager = DatabaseManager(DB_URI)
        db_manager.connect()
        schema = db_manager.get_schema()
        logger.info(f"Database connected for user: {current_user['username']}")
        return {"status": "success", "message": "Database connected successfully", "schema": schema}
    except Exception as e:
        logger.error(f"Database connection failed for user {current_user['username']}: {e}")
        raise HTTPException(status_code=500, detail=f"Database connection failed: {str(e)}")

@app.post("/documents/upload")
async def upload_document(file: UploadFile = File(...), current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        role = current_user["role"]
        default_doc = db.query(DefaultDoc).filter(DefaultDoc.role == role, DefaultDoc.filename == file.filename).first()
        if not default_doc:
            logger.error(f"Unauthorized upload attempt: {file.filename} by user {current_user['username']} with role {role}")
            raise HTTPException(status_code=403, detail=f"User role '{role}' not authorized to upload {file.filename}")
        role_folder = os.path.join(DOC_FOLDER, role)
        os.makedirs(role_folder, exist_ok=True)
        file_path = os.path.join(role_folder, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        db.add(DocumentUpload(
            username=current_user["username"],
            filename=file.filename,
            role=role,
            file_path=file_path,
            timestamp=datetime.utcnow()
        ))
        db.commit()
        doc_processor = DocumentProcessor(DOC_FOLDER, role)
        vector_store = doc_processor.process_documents()
        logger.info(f"Document uploaded and processed: {file.filename} for role {role} by user {current_user['username']}")
        return {
            "status": "success",
            "message": f"Document {file.filename} uploaded and processed for role {role}",
            "filename": file.filename
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Document upload failed for user {current_user['username']}: {e}")
        raise HTTPException(status_code=500, detail=f"Document upload failed: {str(e)}")

@app.post("/query")
async def agent_query(request: QueryRequest, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        role = current_user["role"]
        doc_processor = DocumentProcessor(DOC_FOLDER, role)
        vector_store = doc_processor.process_documents()
        db_manager = DatabaseManager(DB_URI)
        db_manager.connect()
        agent = QueryAgent(db_manager, vector_store)
        response = agent.execute_query(request.query)
        session = db.query(UserSession).filter(UserSession.username == current_user["username"]).first()
        db.add(ChatHistory(
            session_id=session.session_id,
            query_type="agent_query",
            query=request.query,
            response=response,
            timestamp=datetime.utcnow()
        ))
        db.commit()
        logger.info(f"Agent query executed by user {current_user['username']}: {request.query}")
        return {
            "status": "success",
            "query": request.query,
            "response": response
        }
    except Exception as e:
        logger.error(f"Agent query failed for user {current_user['username']}: {e}")
        raise HTTPException(status_code=500, detail=f"Agent query failed: {str(e)}")

@app.post("/documents/query")
async def doc_query(request: QueryRequest, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        role = current_user["role"]
        doc_processor = DocumentProcessor(DOC_FOLDER, role)
        vector_store = doc_processor.process_documents()
        doc_query_handler = DocumentQuery(vector_store)
        response = doc_query_handler.execute_query(request.query)
        session = db.query(UserSession).filter(UserSession.username == current_user["username"]).first()
        db.add(ChatHistory(
            session_id=session.session_id,
            query_type="doc_query",
            query=request.query,
            response=response,
            timestamp=datetime.utcnow()
        ))
        db.commit()
        logger.info(f"Document query executed by user {current_user['username']}: {request.query}")
        return {
            "status": "success",
            "query": request.query,
            "response": response
        }
    except Exception as e:
        logger.error(f"Document query failed for user {current_user['username']}: {e}")
        raise HTTPException(status_code=500, detail=f"Document query failed: {str(e)}")

@app.post("/db/query")
async def db_query(request: QueryRequest, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        db_manager = DatabaseManager(DB_URI)
        db_manager.connect()
        db_query_handler = DatabaseQuery(db_manager)
        result = db_query_handler.execute_query(request.query)
        session = db.query(UserSession).filter(UserSession.username == current_user["username"]).first()
        db.add(ChatHistory(
            session_id=session.session_id,
            query_type="db_query",
            query=request.query,
            response=result["natural_language_response"],
            timestamp=datetime.utcnow()
        ))
        db.commit()
        logger.info(f"Database query executed by user {current_user['username']}: {request.query}")
        return {
            "status": "success",
            "query": request.query,
            "sql_query": result["sql_query"],
            "raw_response": result["raw_response"],
            "natural_language_response": result["natural_language_response"]
        }
    except Exception as e:
        logger.error(f"Database query failed for user {current_user['username']}: {e}")
        raise HTTPException(status_code=500, detail=f"Database query failed: {str(e)}")

if __name__ == "__main__":
    try:
        import uvicorn
        uvicorn.run(app, host="localhost", port=8080)
    except Exception as e:
        logger.error(f"Server startup failed: {e}")
        raise