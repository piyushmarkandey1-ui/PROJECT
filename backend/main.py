import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from core.config import get_settings
from database.company_db import create_tables, init_db

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # ── Startup ──────────────────────────────────────────────────────────
    logger.info("Starting Multi-Tenant Customer Care Bot API…")
    settings = get_settings()

    if not settings.GEMINI_API_KEY:
        print("WARNING: GEMINI_API_KEY is not set. Chat will not work.")
        logger.warning("GEMINI_API_KEY is missing from environment")

    # Initialize database
    init_db()
    create_tables()
    print("Database initialized and tables created")

    print("Multi-Tenant Customer Care Bot API is ready")
    print(f"   Docs: http://localhost:{settings.PORT}/docs")

    yield

    # ── Shutdown ─────────────────────────────────────────────────────────
    logger.info("Shutting down Multi-Tenant Customer Care Bot API")


app = FastAPI(
    title="Multi-Tenant Customer Care Bot API",
    description="AI-powered multi-tenant customer care chatbot — RAG + Gemini Flash + ChromaDB",
    version="2.0.0",
    lifespan=lifespan,
)

# CORS — wide open for hackathon demo
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import router after app is created to avoid circular imports
from services.chatservice.router import router as chat_router  # noqa: E402
app.include_router(chat_router, prefix="/api")


@app.get("/")
async def root():
    return {
        "message": "Multi-Tenant Customer Care Bot API",
        "docs": "/docs",
        "health": "/api/health",
        "status": "running",
    }


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error("Unhandled exception on %s: %s", request.url.path, exc)
    return JSONResponse(
        status_code=500,
        content={"error": str(exc), "status": "error"},
    )


if __name__ == "__main__":
    import uvicorn
    settings = get_settings()
    uvicorn.run("main:app", host="0.0.0.0", port=settings.PORT, reload=True)
