import hashlib
import logging
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from database.db import get_db_session
from database.models import Company
from models.schemas import Company as CompanySchema
from models.schemas import CompanyCreate

logger = logging.getLogger(__name__)


def _hash_api_key(api_key: str) -> str:
    """Hash an API key using SHA-256."""
    return hashlib.sha256(api_key.encode("utf-8")).hexdigest()


def create_company(company_create: CompanyCreate) -> CompanySchema:
    """Create a new company profile."""
    with get_db_session() as session:
        existing = session.query(Company).filter(Company.slug == company_create.slug).first()
        if existing:
            raise ValueError(f"Company with slug '{company_create.slug}' already exists")

        company_id = str(uuid.uuid4())
        now = datetime.utcnow()
        api_key_hash = _hash_api_key(company_create.api_key)

        db_company = Company(
            id=company_id,
            name=company_create.name,
            slug=company_create.slug,
            email=company_create.email,
            contact_phone=company_create.contact_phone,
            api_key_hash=api_key_hash,
            created_at=now,
            updated_at=now,
        )

        session.add(db_company)
        session.flush()

        logger.info("Created company: %s (slug: %s)", company_create.name, company_create.slug)
        return CompanySchema(
            id=company_id,
            name=company_create.name,
            slug=company_create.slug,
            email=company_create.email,
            contact_phone=company_create.contact_phone,
            created_at=now,
            updated_at=now,
        )


def get_company_by_slug(slug: str) -> Optional[CompanySchema]:
    """Get company by slug."""
    with get_db_session() as session:
        company = session.query(Company).filter(Company.slug == slug).first()
        if not company:
            return None
        return CompanySchema(
            id=company.id,
            name=company.name,
            slug=company.slug,
            email=company.email,
            contact_phone=company.contact_phone,
            created_at=company.created_at,
            updated_at=company.updated_at,
        )


def get_company_by_id(company_id: str) -> Optional[CompanySchema]:
    """Get company by ID."""
    with get_db_session() as session:
        company = session.query(Company).filter(Company.id == company_id).first()
        if not company:
            return None
        return CompanySchema(
            id=company.id,
            name=company.name,
            slug=company.slug,
            email=company.email,
            contact_phone=company.contact_phone,
            created_at=company.created_at,
            updated_at=company.updated_at,
        )


def get_company_by_api_key(api_key: str) -> Optional[CompanySchema]:
    """Get company by API key."""
    api_key_hash = _hash_api_key(api_key)
    with get_db_session() as session:
        company = session.query(Company).filter(Company.api_key_hash == api_key_hash).first()
        if not company:
            return None
        return CompanySchema(
            id=company.id,
            name=company.name,
            slug=company.slug,
            email=company.email,
            contact_phone=company.contact_phone,
            created_at=company.created_at,
            updated_at=company.updated_at,
        )


def update_company(slug: str, company_data: dict) -> Optional[CompanySchema]:
    """Update company profile."""
    with get_db_session() as session:
        company = session.query(Company).filter(Company.slug == slug).first()
        if not company:
            return None

        update_data = {k: v for k, v in company_data.items() if k in ["name", "email", "contact_phone"]}
        update_data["updated_at"] = datetime.utcnow()

        for key, value in update_data.items():
            setattr(company, key, value)

        session.flush()

        logger.info("Updated company: %s", slug)
        return CompanySchema(
            id=company.id,
            name=company.name,
            slug=company.slug,
            email=company.email,
            contact_phone=company.contact_phone,
            created_at=company.created_at,
            updated_at=company.updated_at,
        )


def delete_company(slug: str) -> bool:
    """Delete a company."""
    with get_db_session() as session:
        company = session.query(Company).filter(Company.slug == slug).first()
        if not company:
            return False

        session.delete(company)
        logger.info("Deleted company: %s", slug)
        return True


def list_companies() -> list[CompanySchema]:
    """List all companies."""
    with get_db_session() as session:
        companies = session.query(Company).all()
        return [
            CompanySchema(
                id=c.id,
                name=c.name,
                slug=c.slug,
                email=c.email,
                contact_phone=c.contact_phone,
                created_at=c.created_at,
                updated_at=c.updated_at,
            )
            for c in companies
        ]
