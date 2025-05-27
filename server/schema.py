from datetime import datetime
from pydantic import BaseModel
from typing import Dict, Any, Optional

class QueryRequest(BaseModel):
    query: str

class UserModel(BaseModel):
    email: str
    name: str
    username: str
    password: str
    role: str

class Token(BaseModel):
    access_token: str
    token_type: str

class StandardResponse(BaseModel):
    status: str
    message: str
    data: Dict[str, Any] = {}

class DocumentUploadResponse(BaseModel):
    filename: str
    role: str
    timestamp: datetime

class QueryResponse(BaseModel):
    query: str
    response: str

class DatabaseQueryResponse(BaseModel):
    query: str
    sql_query: Optional[str] = None
    raw_response: Optional[Dict[str, Any]] = None
    natural_language_response: str