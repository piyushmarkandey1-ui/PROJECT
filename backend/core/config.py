from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    GEMINI_API_KEY: str = ""
    GOOGLE_API_KEY: str = ""
    EMBEDDING_MODEL: str = "models/text-embedding-004"
    LLM_MODEL: str = "gemini-2.0-flash"
    CHROMA_PERSIST_PATH: str = "./chromadb_store"
    MAX_TOKENS: int = 2000
    CONFIDENCE_THRESHOLD: float = 0.70
    PORT: int = 8000
    FRONTEND_URL: str = "http://localhost:3000"
    SECRET_KEY: str = "changeme"
    DATABASE_URL: str = "sqlite:///./customer_care_bot.db"

    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
