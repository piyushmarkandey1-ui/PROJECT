import logging
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader

from database.company_store import get_company_by_api_key
from models.schemas import Company

logger = logging.getLogger(__name__)

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def get_current_company(api_key: Optional[str] = Depends(api_key_header)) -> Company:
    """Dependency to get the current company from API key."""
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API key in X-API-Key header",
        )
    
    company = get_company_by_api_key(api_key)
    if not company:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
        )
    
    return company
