"""
Pydantic schemas for request/response validation.

Company creation flow:
  - CompanyCreate  → input (no api_key needed — auto-generated)
  - CompanyCreateResponse → output (includes api_key shown ONCE)
  - Company        → all other responses (no api_key)

Chat flow:
  - ChatRequest    → POST /api/chat and /api/chat/stream
  - ChatResponse   → POST /api/chat (full JSON)
  - SSE stream     → POST /api/chat/stream (token events + done event)
"""
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field


# ─── Company ──────────────────────────────────────────────────────────────────

class CompanyBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    slug: Optional[str] = Field(
        None,
        description="URL-safe identifier (auto-generated from name if not provided)"
    )
    email: EmailStr
    contact_phone: Optional[str] = None


class CompanyCreate(CompanyBase):
    """
    Company creation request.
    API key is auto-generated server-side — do not include it in the request.
    Slug is optional — auto-derived from name if omitted.
    Password is optional — if provided, enables email/password authentication.
    """
    password: Optional[str] = Field(None, min_length=8, max_length=100)


class CompanyCreateResponse(BaseModel):
    """
    Response returned once when a company is created.
    The api_key is the plaintext key — store it immediately.
    It is hashed and stored server-side; the plaintext is never shown again.
    """
    id: str
    name: str
    slug: str
    email: str
    contact_phone: Optional[str] = None
    api_key: str = Field(
        description="Plaintext API key — shown ONCE at creation, never retrievable again"
    )
    created_at: datetime
    updated_at: datetime


class Company(CompanyBase):
    """Company profile (no api_key — use CompanyCreateResponse for initial creation)."""
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CompanyUpdate(BaseModel):
    """Partial update — only provided fields are changed."""
    name: Optional[str] = None
    email: Optional[str] = None
    contact_phone: Optional[str] = None


class CompanyListResponse(BaseModel):
    companies: List[Company]
    count: int


# ─── Chat ─────────────────────────────────────────────────────────────────────

class ChatRequest(BaseModel):
    """
    Request body for both /api/chat and /api/chat/stream.
    session_id is optional — a new session is created if not provided or expired.
    """
    session_id: Optional[str] = None
    message: str = Field(..., min_length=1)
    company_slug: str = Field(
        ...,
        description="Company slug — determines which knowledge base and session space to use"
    )


class ChatResponse(BaseModel):
    """
    Full JSON response from /api/chat.
    For streaming, use /api/chat/stream which sends SSE events instead.

    confidence: 0.85 = relevant KB docs found; 0.55 = no relevant docs
    is_escalated: True if escalation engine triggered (response is escalation message)
    retrieved_sources: list of source file paths used in RAG context
    """
    session_id: str
    response: str
    confidence: float
    is_escalated: bool
    escalation_reason: Optional[str] = None
    retrieved_sources: List[str] = []
    turn_count: int
    timestamp: datetime


# ─── Session ──────────────────────────────────────────────────────────────────

class SessionCreateResponse(BaseModel):
    session_id: str
    created_at: datetime


class SessionHistoryResponse(BaseModel):
    session_id: str
    messages: List[dict]  # [{"role": "user"|"assistant", "content": str}]
    count: int


# ─── Knowledge Base ───────────────────────────────────────────────────────────

class KnowledgeUploadResponse(BaseModel):
    message: str
    documents_added: int


class KnowledgeStatsResponse(BaseModel):
    total_documents: int
    status: str  # "ready" | "empty"


# ─── Health ───────────────────────────────────────────────────────────────────

class HealthResponse(BaseModel):
    status: str  # "healthy"
    timestamp: datetime
    model: str   # current primary LLM model name
    knowledge_base_docs: int


# ─── Authentication ───────────────────────────────────────────────────────────

class LoginRequest(BaseModel):
    """Login request with email and password."""
    email: EmailStr
    password: str = Field(..., min_length=1)


class LoginResponse(BaseModel):
    """Login response with JWT access token."""
    access_token: str
    token_type: str = "bearer"
    company: Company
