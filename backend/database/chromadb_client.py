import logging
import re
from typing import Any, Dict, List, Optional

import chromadb

from core.config import get_settings

logger = logging.getLogger(__name__)

_client: Optional[chromadb.PersistentClient] = None
_collections: Dict[str, Any] = {}


def _get_client() -> chromadb.PersistentClient:
    global _client
    if _client is None:
        settings = get_settings()
        try:
            _client = chromadb.PersistentClient(path=settings.CHROMA_PERSIST_PATH)
            logger.info("ChromaDB client initialised at %s", settings.CHROMA_PERSIST_PATH)
        except Exception as e:
            logger.error("Failed to initialise ChromaDB client: %s", e)
            raise
    return _client


def _sanitize_collection_name(name: str) -> str:
    """Sanitize name to be valid ChromaDB collection name.
    
    ChromaDB collection names must:
    - Start with a letter or underscore
    - Contain only letters, numbers, underscores, or hyphens
    - Be 3-63 characters long
    """
    sanitized = re.sub(r"[^a-zA-Z0-9_-]", "_", name)
    if not sanitized or not sanitized[0].isalpha() and sanitized[0] != "_":
        sanitized = f"kb_{sanitized}"
    if len(sanitized) < 3:
        sanitized = sanitized.ljust(3, "_")
    if len(sanitized) > 63:
        sanitized = sanitized[:63]
    return sanitized


def get_collection(company_slug: str):
    """Return (or create) a company-specific collection."""
    collection_name = _sanitize_collection_name(f"kb_{company_slug}")
    
    if collection_name not in _collections:
        client = _get_client()
        try:
            _collections[collection_name] = client.get_or_create_collection(
                name=collection_name,
                metadata={"hnsw:space": "cosine", "company_slug": company_slug},
            )
            logger.info(
                "ChromaDB collection '%s' ready — %d docs",
                collection_name,
                _collections[collection_name].count(),
            )
        except Exception as e:
            logger.error("Failed to get/create ChromaDB collection: %s", e)
            raise
    
    return _collections[collection_name]


def add_documents(
    company_slug: str,
    texts: List[str],
    metadatas: List[Dict[str, Any]],
    ids: List[str],
) -> None:
    try:
        collection = get_collection(company_slug)
        collection.add(documents=texts, metadatas=metadatas, ids=ids)
        logger.info("Added %d documents to company '%s' collection", len(texts), company_slug)
    except Exception as e:
        logger.error("Failed to add documents: %s", e)
        raise


def query_documents(company_slug: str, query_text: str, n_results: int = 3) -> List[str]:
    try:
        collection = get_collection(company_slug)
        count = collection.count()
        if count == 0:
            return []
        results = collection.query(
            query_texts=[query_text],
            n_results=min(n_results, count),
        )
        docs = results.get("documents", [[]])[0]
        logger.info("Retrieved %d documents for company '%s'", len(docs), company_slug)
        return docs
    except Exception as e:
        logger.error("Failed to query ChromaDB: %s", e)
        return []


def delete_collection(company_slug: str) -> None:
    collection_name = _sanitize_collection_name(f"kb_{company_slug}")
    try:
        client = _get_client()
        client.delete_collection(collection_name)
        if collection_name in _collections:
            del _collections[collection_name]
        logger.info("ChromaDB collection '%s' deleted for company '%s'", collection_name, company_slug)
    except Exception as e:
        logger.error("Failed to delete ChromaDB collection: %s", e)
        raise


def get_document_count(company_slug: str) -> int:
    try:
        collection = get_collection(company_slug)
        return collection.count()
    except Exception as e:
        logger.error("Failed to get document count: %s", e)
        return 0


def reset_collection(company_slug: str) -> None:
    """Drop and recreate a company's collection — useful for re-seeding."""
    collection_name = _sanitize_collection_name(f"kb_{company_slug}")
    try:
        client = _get_client()
        client.delete_collection(collection_name)
        if collection_name in _collections:
            del _collections[collection_name]
        get_collection(company_slug)  # recreate
        logger.info("ChromaDB collection '%s' reset for company '%s'", collection_name, company_slug)
    except Exception as e:
        logger.error("Failed to reset collection: %s", e)
        raise
