import logging
import os
import shutil
import tempfile
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status

from core.auth import get_current_company
from core.config import get_settings
from database.chromadb_client import get_document_count, reset_collection
from database.company_store import (
    create_company,
    delete_company,
    get_company_by_slug,
    list_companies,
    update_company,
)
from models.schemas import (
    ChatRequest,
    ChatResponse,
    Company,
    CompanyCreate,
    CompanyListResponse,
    CompanyUpdate,
    HealthResponse,
    KnowledgeStatsResponse,
    KnowledgeUploadResponse,
    SessionCreateResponse,
    SessionHistoryResponse,
)
from services.chatservice.handler import ChatHandler
from services.ragservice.embedder import KnowledgeBaseBuilder
from services.sessionservice.memory import SessionManager

logger = logging.getLogger(__name__)
router = APIRouter()

_chat_handler: Optional[ChatHandler] = None
_session_manager = SessionManager()
_kb_builder = KnowledgeBaseBuilder()


def _get_chat_handler() -> ChatHandler:
    global _chat_handler
    if _chat_handler is None:
        _chat_handler = ChatHandler()
    return _chat_handler


# ---------------------------------------------------------------------------
# Company management
# ---------------------------------------------------------------------------

@router.post("/companies", response_model=Company, status_code=status.HTTP_201_CREATED)
async def create_company_endpoint(company: CompanyCreate):
    """Create a new company profile."""
    try:
        return create_company(company)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/companies", response_model=CompanyListResponse)
async def list_companies_endpoint():
    """List all companies (admin endpoint)."""
    companies = list_companies()
    return CompanyListResponse(companies=companies, count=len(companies))


@router.get("/companies/{slug}", response_model=Company)
async def get_company_endpoint(slug: str):
    """Get a company by slug."""
    company = get_company_by_slug(slug)
    if not company:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")
    return company


@router.put("/companies/{slug}", response_model=Company)
async def update_company_endpoint(
    slug: str,
    company_update: CompanyUpdate,
    current_company: Company = Depends(get_current_company),
):
    """Update a company profile (only accessible by the company itself)."""
    if current_company.slug != slug:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own company profile",
        )
    
    updated = update_company(slug, company_update.model_dump(exclude_unset=True))
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")
    return updated


@router.delete("/companies/{slug}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_company_endpoint(
    slug: str,
    current_company: Company = Depends(get_current_company),
):
    """Delete a company (only accessible by the company itself)."""
    if current_company.slug != slug:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own company",
        )
    
    success = delete_company(slug)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")
    
    try:
        reset_collection(slug)
    except Exception:
        pass
    
    return None


# ---------------------------------------------------------------------------
# Chat
# ---------------------------------------------------------------------------

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Send a chat message using a company's knowledge base."""
    company = get_company_by_slug(request.company_slug)
    if not company:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")
    
    try:
        session_id = request.session_id
        if not session_id or not _session_manager.session_exists(request.company_slug, session_id):
            session_id = _session_manager.create_session(request.company_slug, session_id or None)

        handler = _get_chat_handler()
        response = await handler.process_message(
            session_id=session_id,
            user_message=request.message,
            company_slug=request.company_slug,
            company_name=company.name,
        )
        return response
    except Exception as e:
        logger.error("Chat endpoint error: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------------------------------------------------------
# Session management (company-aware)
# ---------------------------------------------------------------------------

@router.post("/session/new", response_model=SessionCreateResponse)
async def new_session(company_slug: str):
    """Create a new session tied to a specific company."""
    session_id = _session_manager.create_session(company_slug)
    return SessionCreateResponse(session_id=session_id, created_at=datetime.utcnow())


@router.get("/session/{company_slug}/{session_id}/history", response_model=SessionHistoryResponse)
async def get_history(company_slug: str, session_id: str):
    """Get session history - only accessible for the correct company."""
    if not _session_manager.session_exists(company_slug, session_id):
        raise HTTPException(status_code=404, detail="Session not found or expired")
    messages = _session_manager.get_history(company_slug, session_id)
    return SessionHistoryResponse(
        session_id=session_id, messages=messages, count=len(messages)
    )


@router.delete("/session/{company_slug}/{session_id}")
async def clear_session(company_slug: str, session_id: str):
    """Clear a session - only for the correct company."""
    _session_manager.clear_session(company_slug, session_id)
    return {"message": "Session cleared"}


# ---------------------------------------------------------------------------
# Knowledge base (company-specific)
# ---------------------------------------------------------------------------

@router.post("/knowledge/upload-csv", response_model=KnowledgeUploadResponse)
async def upload_csv(
    file: UploadFile = File(...),
    current_company: Company = Depends(get_current_company),
):
    """Upload a CSV to the current company's knowledge base."""
    if not (file.filename or "").endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are accepted")
    tmp_path: Optional[str] = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp:
            shutil.copyfileobj(file.file, tmp)
            tmp_path = tmp.name

        count = _kb_builder.build_from_csv(
            tmp_path,
            company_slug=current_company.slug,
            force_reload=True,
        )
        return KnowledgeUploadResponse(
            message=f"Successfully added {count} documents to {current_company.name}'s knowledge base",
            documents_added=count,
        )
    except Exception as e:
        logger.error("CSV upload failed: %s", e)
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)


@router.get("/knowledge/stats", response_model=KnowledgeStatsResponse)
async def knowledge_stats(
    company_slug: Optional[str] = None,
    current_company: Optional[Company] = Depends(get_current_company),
):
    """Get knowledge base stats. If no company_slug provided, uses current company."""
    slug = company_slug or current_company.slug
    count = get_document_count(slug)
    return KnowledgeStatsResponse(
        total_documents=count,
        status="ready" if count > 0 else "empty",
    )


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------

@router.get("/health", response_model=HealthResponse)
async def health():
    settings = get_settings()
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow(),
        model=settings.LLM_MODEL,
        knowledge_base_docs=0,
    )
