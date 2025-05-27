# server/models.py
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
from zoneinfo import ZoneInfo
from config import logger,CONFIG
from sqlalchemy import create_engine

Base = declarative_base()
SQLITE_DB = CONFIG['SQLITE_DB']

def get_db_session():
    try:
        engine = create_engine(SQLITE_DB, echo=False)
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        return Session()
    except Exception as e:
        logger.error(f"Failed to initialize database session: {e}", exc_info=True)
        raise RuntimeError("Database initialization failed")

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    role = Column(String, nullable=False)
    signup_timestamp = Column(DateTime, nullable=False, default=lambda: datetime.now(ZoneInfo("Asia/Kolkata")))
    chat_history = relationship("ChatHistory", back_populates="user")
    sessions = relationship("UserSession", back_populates="user")
    logs = relationship("UserLog", back_populates="user")
    uploaded_documents = relationship("Documents", back_populates="user")

class UserSession(Base):
    __tablename__ = "sessions"
    session_id = Column(String, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    token = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(ZoneInfo("Asia/Kolkata")))
    expires_at = Column(DateTime, nullable=False)
    status = Column(String, nullable=False, default="active")  # active, expired
    user = relationship("User", back_populates="sessions")

class UserLog(Base):
    __tablename__ = "user_logs"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    login_timestamp = Column(DateTime, default=lambda: datetime.now(ZoneInfo("Asia/Kolkata")))
    client_ip = Column(String, nullable=False)
    mac_address = Column(String, nullable=True)
    os_info = Column(String, nullable=True)
    browser = Column(String, nullable=True)
    device = Column(String, nullable=True)
    user_agent = Column(Text, nullable=True)
    memory_gb = Column(Float, nullable=True)
    cpu_cores = Column(Integer, nullable=True)
    user = relationship("User", back_populates="logs")

class Documents(Base):
    __tablename__ = "documents"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True)  # Nullable for default documents
    filename = Column(String, nullable=False)
    role = Column(String, nullable=False)
    file_path = Column(String, nullable=True)  # Nullable for default documents not yet processed
    doc_type = Column(String, nullable=False)  # uploaded, default
    timestamp = Column(DateTime, nullable=False, default=lambda: datetime.now(ZoneInfo("Asia/Kolkata")))
    user = relationship("User", back_populates="uploaded_documents")

class ChatHistory(Base):
    __tablename__ = "chat_history"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    query = Column(Text, nullable=False)
    response = Column(Text, nullable=False)
    response_id = Column(String, unique=True, index=True, nullable=False)
    query_type = Column(String, nullable=False, default="agent")  # agent, db, doc
    query_processing_time = Column(Float, nullable=True)  # in seconds
    chat_timestamp = Column(DateTime, default=lambda: datetime.now(ZoneInfo("Asia/Kolkata")))
    user = relationship("User", back_populates="chat_history")