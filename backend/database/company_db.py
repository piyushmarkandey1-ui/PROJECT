"""
Company database module.

This keeps company profiles (slug, name, email, hashed API key) isolated from
other backend persistence concerns.
"""

import logging
from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from core.config import get_settings

logger = logging.getLogger(__name__)

Base = declarative_base()

_engine = None
_session_factory: sessionmaker | None = None


def init_db() -> None:
    """Initialize company database engine and session factory."""
    global _engine, _session_factory
    settings = get_settings()

    if _engine is None:
        _engine = create_engine(
            settings.COMPANY_DATABASE_URL,
            connect_args={"check_same_thread": False} if "sqlite" in settings.COMPANY_DATABASE_URL else {},
            pool_pre_ping=True,
            pool_recycle=3600,
        )
        _session_factory = sessionmaker(autocommit=False, autoflush=False, bind=_engine)
        logger.info("Company database initialised with URL: %s", settings.COMPANY_DATABASE_URL)


def create_tables() -> None:
    """Create company tables."""
    if _engine is None:
        init_db()
    Base.metadata.create_all(bind=_engine)
    logger.info("Company tables created")


@contextmanager
def get_db_session() -> Generator[Session, None, None]:
    """Context manager to get a company database session."""
    if _session_factory is None:
        init_db()

    session = _session_factory()  # type: ignore[misc]
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

