"""
Company CRUD operations and API key / slug generation.

Key functions:
  create_company()        — auto-generates slug + API key, stores hash
  get_company_by_api_key()— hashes the provided key and looks up by hash
  get_company_by_slug()   — public lookup (no auth required)
  update_company()        — only name, email, contact_phone are updatable
  delete_company()        — also triggers ChromaDB collection deletion in router

API key lifecycle:
  1. _generate_api_key()  → 32-char cryptographically secure random string
  2. _hash_api_key()      → SHA-256 hex digest stored in DB
  3. Plaintext returned once in CompanyCreateResponse — never stored
"""
import hashlib
import logging
import secrets
import string
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from database.db import get_db_session
from database.models import Company
from models.schemas import Company as CompanySchema
from models.schemas import CompanyCreate, CompanyCreateResponse

logger = logging.getLogger(__name__)


def _generate_api_key(length: int = 32) -> str:
    """Generate a secure random API key."""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def _hash_api_key(api_key: str) -> str:
    """Hash an API key using SHA-256."""
    return hashlib.sha256(api_key.encode("utf-8")).hexdigest()


def _generate_slug(name: str) -> str:
    """Generate URL-safe slug from company name."""
    # Convert to lowercase, replace spaces with hyphens, remove special chars
    slug = name.lower().strip()
    slug = ''.join(c if c.isalnum() or c == ' ' else '-' for c in slug)
    slug = slug.replace(' ', '-').replace('--', '-')
    # Remove trailing hyphens
    slug = slug.rstrip('-')
    # Ensure minimum length
    if len(slug) < 3:
        slug = slug + str(uuid.uuid4())[:3]
    return slug[:50]


def create_company(company_create: CompanyCreate) -> CompanyCreateResponse:
    """Create a new company profile with auto-generated API key and slug."""
    with get_db_session() as session:
        # Generate slug if not provided
        slug = company_create.slug or _generate_slug(company_create.name)
        
        # Check if slug already exists
        existing = session.query(Company).filter(Company.slug == slug).first()
        if existing:
            # Append timestamp to make unique
            slug = f"{slug}-{int(datetime.utcnow().timestamp())}"
        
        # Auto-generate API key
        api_key = _generate_api_key(32)
        api_key_hash = _hash_api_key(api_key)
        
        company_id = str(uuid.uuid4())
        now = datetime.utcnow()

        db_company = Company(
            id=company_id,
            name=company_create.name,
            slug=slug,
            email=company_create.email,
            contact_phone=company_create.contact_phone,
            api_key_hash=api_key_hash,
            created_at=now,
            updated_at=now,
        )

        session.add(db_company)
        session.flush()

        logger.info("Created company: %s (slug: %s)", company_create.name, slug)
        
        # Return response with API key (only shown once!)
        return CompanyCreateResponse(
            id=company_id,
            name=company_create.name,
            slug=slug,
            email=company_create.email,
            contact_phone=company_create.contact_phone,
            api_key=api_key,
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
