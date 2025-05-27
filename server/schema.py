from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional, List, Dict, Any

class StandardResponse(BaseModel):
    status: str
    message: str
    data: Optional[Dict[str, Any]] = None

class UserModel(BaseModel):
    email: EmailStr
    name: str
    username: str
    password: str = Field(..., min_length=8)
    role: str

class Token(BaseModel):
    access_token: str
    token_type: str

class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    query: str
    response: str

class DatabaseQueryResponse(BaseModel):
    query: str
    sql_query: str
    raw_response: List[Dict[str, Any]]
    natural_language_response: str

class DocumentUploadResponse(BaseModel):
    filename: str
    role: str
    timestamp: datetime