import logging
from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker

from core.config import get_settings

logger = logging.getLogger(__name__)

Base = declarative_base()

_engine = None
_session_factory = None


def init_db() -> None:
    """Initialize the database engine and session factory."""
    global _engine, _session_factory
    settings = get_settings()
    
    if _engine is None:
        _engine = create_engine(
            settings.DATABASE_URL,
            connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {},
            pool_pre_ping=True,
            pool_recycle=3600,
        )
        _session_factory = sessionmaker(autocommit=False, autoflush=False, bind=_engine)
        logger.info("Database initialized with URL: %s", settings.DATABASE_URL)


def create_tables() -> None:
    """Create all database tables."""
    if _engine is None:
        init_db()
    Base.metadata.create_all(bind=_engine)
    logger.info("Database tables created")


@contextmanager
def get_db_session() -> Generator[Session, None, None]:
    """Context manager to get a database session."""
    if _session_factory is None:
        init_db()
    
    session = _session_factory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
