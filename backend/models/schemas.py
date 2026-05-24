from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field


class CompanyBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    slug: str = Field(..., min_length=2, max_length=50, description="URL-safe company identifier")
    email: EmailStr
    contact_phone: Optional[str] = None


class CompanyCreate(CompanyBase):
    api_key: str = Field(..., min_length=32, description="Company API key for authentication")


class Company(CompanyBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ChatRequest(BaseModel):
    session_id: Optional[str] = None
    message: str
    company_slug: str = Field(..., description="Company slug to identify which knowledge base to use")


class ChatResponse(BaseModel):
    session_id: str
    response: str
    confidence: float
    is_escalated: bool
    escalation_reason: Optional[str] = None
    retrieved_sources: List[str] = []
    turn_count: int
    timestamp: datetime


class SessionCreateResponse(BaseModel):
    session_id: str
    created_at: datetime


class SessionHistoryResponse(BaseModel):
    session_id: str
    messages: List[dict]
    count: int


class KnowledgeUploadResponse(BaseModel):
    message: str
    documents_added: int


class KnowledgeStatsResponse(BaseModel):
    total_documents: int
    status: str


class HealthResponse(BaseModel):
    status: str
    timestamp: datetime
    model: str
    knowledge_base_docs: int


class CompanyListResponse(BaseModel):
    companies: List[Company]
    count: int


class CompanyUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    contact_phone: Optional[str] = None
