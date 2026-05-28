"""
Authentication dependency for FastAPI endpoints.

Supports both API key and JWT token authentication.

Usage:
    @router.put("/companies/{slug}")
    async def update(slug: str, company: Company = Depends(get_current_company)):
        ...

Authentication methods:
1. X-API-Key header: SHA-256 hashed and looked up in the companies table
2. Authorization header: Bearer token (JWT) for email/password authentication

Returns the matching Company schema or raises HTTP 401.
"""
import logging
from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader, HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from pydantic import ValidationError

from core.config import get_settings
from database.company_store import get_company_by_api_key
from models.schemas import Company

logger = logging.getLogger(__name__)

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)
bearer_scheme = HTTPBearer(auto_error=False)


def create_access_token(company_id: str, company_slug: str) -> str:
    """Create a JWT access token for a company."""
    settings = get_settings()
    expire = datetime.utcnow() + timedelta(hours=24)
    to_encode = {
        "sub": company_id,
        "slug": company_slug,
        "exp": expire,
        "type": "access"
    }
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")
    return encoded_jwt


def verify_token(token: str) -> Optional[dict]:
    """Verify a JWT token and return the payload if valid."""
    settings = get_settings()
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        return payload
    except JWTError:
        return None


async def get_current_company(
    api_key: Optional[str] = Depends(api_key_header),
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme)
) -> Company:
    """Dependency to get the current company from API key or JWT token."""
    
    # Try API key authentication first
    if api_key:
        company = get_company_by_api_key(api_key)
        if company:
            return company
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid API key",
            )
    
    # Try JWT token authentication
    if credentials and credentials.scheme == "Bearer":
        token = credentials.credentials
        payload = verify_token(token)
        if payload:
            from database.company_store import get_company_by_id
            company = get_company_by_id(payload.get("sub"))
            if company:
                return company
            else:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Company not found",
                )
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
            )
    
    # No valid authentication provided
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Missing authentication. Provide X-API-Key header or Authorization: Bearer token.",
    )
