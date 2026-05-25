import json
import logging
import os
import shutil
import tempfile
from datetime import datetime
from typing import AsyncGenerator, Optional

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import StreamingResponse

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
    CompanyCreateResponse,
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

@router.post("/companies", response_model=CompanyCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_company_endpoint(company: CompanyCreate):
    """Create a new company profile with auto-generated API key and slug.
    
    The API key is returned only once - make sure to save it securely.
    """
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


@router.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    """Streaming chat endpoint — sends tokens via Server-Sent Events with model fallback."""
    import os
    from langchain_core.messages import HumanMessage, SystemMessage
    from langchain_google_genai import ChatGoogleGenerativeAI
    from core.guardrails import GuardrailsEngine
    from services.ragservice.retriever import Retriever
    from services.chatservice.handler import _make_llm, _is_quota_error, _extract_chunk_text

    company = get_company_by_slug(request.company_slug)
    if not company:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")

    session_id = request.session_id
    if not session_id or not _session_manager.session_exists(request.company_slug, session_id):
        session_id = _session_manager.create_session(request.company_slug, session_id or None)

    settings = get_settings()
    guardrails = GuardrailsEngine()
    retriever = Retriever()

    # Build context
    session_summary = _session_manager.get_session_summary(request.company_slug, session_id)
    retrieved_docs = retriever.retrieve(request.message, request.company_slug)
    context = retriever.format_context(retrieved_docs)
    is_relevant = retriever.is_relevant(request.message, request.company_slug)
    confidence = 0.85 if is_relevant else 0.55

    system_content = guardrails.get_system_prompt(company.name)
    if context:
        system_content += f"\n\n{context}"
    if session_summary:
        system_content += f"\n\nConversation so far:\n{session_summary}"

    # Build model fallback list
    model_chain = [settings.LLM_MODEL] + settings.fallback_model_list

    async def token_generator() -> AsyncGenerator[str, None]:
        full_response = []
        succeeded = False

        for model_name in model_chain:
            full_response = []
            try:
                llm = _make_llm(model_name, settings)
                messages = [
                    SystemMessage(content=system_content),
                    HumanMessage(content=request.message),
                ]
                async for chunk in llm.astream(messages):
                    text = _extract_chunk_text(chunk.content)
                    if text:
                        full_response.append(text)
                        yield f"data: {json.dumps({'token': text})}\n\n"
                succeeded = True
                logger.info("Stream OK (model=%s, session=%s)", model_name, session_id)
                break  # success — stop trying fallbacks

            except Exception as e:
                error_str = str(e)
                if _is_quota_error(error_str):
                    logger.warning("Quota hit on %s during stream, trying next...", model_name)
                    # Clear any partial tokens already sent — send a reset signal
                    yield f"data: {json.dumps({'reset': True})}\n\n"
                    continue
                else:
                    logger.error("Non-quota stream error on %s: %s", model_name, error_str[:200])
                    break

        if not succeeded:
            msg = "All AI models are currently rate-limited. Please wait a minute and try again."
            yield f"data: {json.dumps({'token': msg, 'error': True})}\n\n"
            full_response = [msg]

        # Persist the full response
        bot_response = guardrails.sanitize_response("".join(full_response))
        _session_manager.add_message(request.company_slug, session_id, "user", request.message)
        _session_manager.add_message(request.company_slug, session_id, "assistant", bot_response)

        sources = list({doc.source for doc in retrieved_docs})
        history = _session_manager.get_history(request.company_slug, session_id)
        yield f"data: {json.dumps({'done': True, 'session_id': session_id, 'confidence': round(confidence, 2), 'sources': sources, 'turn_count': len(history)})}\n\n"

    return StreamingResponse(
        token_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        }
    )


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


# ---------------------------------------------------------------------------
# Demo company creation (for quick testing)
# ---------------------------------------------------------------------------

@router.post("/demo-company", response_model=CompanyCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_demo_company():
    """Create a demo company for testing purposes."""
    from models.schemas import CompanyCreate
    
    demo_company = CompanyCreate(
        name="Demo Corporation",
        slug="demo-corp",
        email="demo@demo.com",
        contact_phone="555-0123"
    )
    
    try:
        return create_company(demo_company)
    except ValueError as e:
        # If demo company already exists, get it
        from database.company_store import get_company_by_slug
        company = get_company_by_slug("demo-corp")
        if company:
            # Return a new API key for demo company
            from database.company_store import _generate_api_key, _hash_api_key
            api_key = _generate_api_key(32)
            api_key_hash = _hash_api_key(api_key)
            
            from database.db import get_db_session
            from database.models import Company
            with get_db_session() as session:
                db_company = session.query(Company).filter(Company.slug == "demo-corp").first()
                if db_company:
                    db_company.api_key_hash = api_key_hash
                    session.flush()
            
            return CompanyCreateResponse(
                id=company.id,
                name=company.name,
                slug=company.slug,
                email=company.email,
                contact_phone=company.contact_phone,
                api_key=api_key,
                created_at=company.created_at,
                updated_at=company.updated_at,
            )
        raise HTTPException(status_code=500, detail=str(e))
