"""
Application settings loaded from .env via pydantic-settings.

Key design notes:
- Both GEMINI_API_KEY and GOOGLE_API_KEY must be set to the same value.
  GEMINI_API_KEY is used by the direct REST fallback path.
  GOOGLE_API_KEY is read by langchain-google-genai automatically.
- LLM_MODEL is the primary model tried first on every request.
- LLM_FALLBACK_MODELS is a comma-separated list of models tried in order
  when the primary (or any fallback) returns HTTP 429 quota exceeded.
- lru_cache ensures Settings is only instantiated once per process.
  After changing .env, restart the server to pick up new values.
"""
from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    GEMINI_API_KEY: str = ""
    GOOGLE_API_KEY: str = ""
    EMBEDDING_MODEL: str = "models/text-embedding-004"

    # Primary model — gemini-3.5-flash has separate quota from 2.x models
    # Fallback chain: 3.5-flash → 3.1-flash-lite → 3-flash-preview → 2.0-flash → 2.0-flash-lite
    LLM_MODEL: str = "gemini-3.5-flash"
    LLM_FALLBACK_MODELS: str = "gemini-3.1-flash-lite,gemini-3-flash-preview,gemini-2.0-flash,gemini-2.0-flash-lite"

    CHROMA_PERSIST_PATH: str = "./chromadb_store"
    MAX_TOKENS: int = 1024
    CONFIDENCE_THRESHOLD: float = 0.70
    PORT: int = 8000
    FRONTEND_URL: str = "http://localhost:3000"
    SECRET_KEY: str = "changeme"
    DATABASE_URL: str = "sqlite:///./customer_care_bot.db"

    @property
    def fallback_model_list(self) -> list[str]:
        return [m.strip() for m in self.LLM_FALLBACK_MODELS.split(",") if m.strip()]

    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
