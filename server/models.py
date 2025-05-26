from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from config import logger

Base = declarative_base()
SQLITE_DB = "sqlite:///users.db"

def get_db_session():
    try:
        engine = create_engine(SQLITE_DB, echo=False)
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        return Session()
    except Exception as e:
        logger.error(f"Failed to initialize database session: {e}")
        raise

class User(Base):
    __tablename__ = "users"
    username = Column(String, primary_key=True)
    hashed_password = Column(String, nullable=False)
    role = Column(String, nullable=False)

class Session(Base):
    __tablename__ = "sessions"
    session_id = Column(String, primary_key=True)
    username = Column(String, ForeignKey("users.username"), nullable=False)
    token = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)

class ChatHistory(Base):
    __tablename__ = "chat_history"
    id = Column(Integer, primary_key=True)
    session_id = Column(String, ForeignKey("sessions.session_id"), nullable=False)
    query_type = Column(String, nullable=False)
    query = Column(String, nullable=False)
    response = Column(String, nullable=False)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)

class LoginActivity(Base):
    __tablename__ = "login_activity"
    id = Column(Integer, primary_key=True)
    username = Column(String, ForeignKey("users.username"), nullable=False)
    action = Column(String, nullable=False)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)

class DocumentUpload(Base):
    __tablename__ = "document_uploads"
    id = Column(Integer, primary_key=True)
    username = Column(String, ForeignKey("users.username"), nullable=False)
    filename = Column(String, nullable=False)
    role = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)

class DefaultDoc(Base):
    __tablename__ = "default_docs"
    id = Column(Integer, primary_key=True)
    role = Column(String, nullable=False)
    filename = Column(String, nullable=False)