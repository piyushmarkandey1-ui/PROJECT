"""
KnowledgeBaseBuilder — ingests documents into ChromaDB.

ChromaDB uses its own built-in embedding model (all-MiniLM-L6-v2 via
sentence-transformers) for both storage and retrieval, which guarantees
consistent vector space.  We do NOT use a separate Google embedding here
to avoid mismatched embedding spaces between add and query.
"""
import logging
import time
import uuid
from datetime import datetime
from typing import List

from database.chromadb_client import (
    add_documents,
    get_document_count,
    reset_collection,
)
from services.ragservice.loader import DocumentLoader

logger = logging.getLogger(__name__)


class KnowledgeBaseBuilder:
    def __init__(self):
        self._loader = DocumentLoader()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _already_seeded(self, company_slug: str) -> bool:
        """Return True if the company's collection already has documents."""
        return get_document_count(company_slug) > 0

    def _store_documents(
        self,
        company_slug: str,
        texts: List[str],
        source: str,
        category: str = "general",
    ) -> int:
        if not texts:
            logger.warning("No documents to store from source: %s for company %s", source, company_slug)
            return 0

        ids = [str(uuid.uuid4()) for _ in texts]
        metadatas = [
            {
                "source": source,
                "category": category,
                "timestamp": datetime.utcnow().isoformat(),
            }
            for _ in texts
        ]

        print(f"  Storing {len(texts)} documents from '{source}' for company '{company_slug}'...")
        logger.info("Storing %d documents from %s for company %s", len(texts), source, company_slug)

        for attempt in range(3):
            try:
                add_documents(company_slug=company_slug, texts=texts, metadatas=metadatas, ids=ids)
                total = get_document_count(company_slug)
                # Avoid emoji characters in console output (Windows cp1252 can crash).
                print(f"  Stored {len(texts)} docs. Total in KB for '{company_slug}': {total}")
                return len(texts)
            except Exception as e:
                wait = 2 ** attempt
                logger.warning(
                    "Attempt %d failed (%s). Retrying in %ds…",
                    attempt + 1,
                    e,
                    wait,
                )
                time.sleep(wait)

        logger.error("All retry attempts failed for source: %s and company: %s", source, company_slug)
        return 0

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def build_from_csv(self, filepath: str, company_slug: str = "default", force_reload: bool = False) -> int:
        """Load a CSV and store its Q&A pairs for a specific company.

        If the collection already has documents and force_reload is False,
        this is a no-op (avoids duplicate entries on every server restart).
        Pass force_reload=True to wipe and re-seed.
        """
        if self._already_seeded(company_slug) and not force_reload:
            count = get_document_count(company_slug)
            logger.info("KB already seeded (%d docs) for company %s. Skipping CSV load.", count, company_slug)
            # Avoid emoji characters in console output (Windows cp1252 can crash).
            print(f"  Info: Knowledge base for '{company_slug}' already has {count} docs - skipping reload.")
            return count

        if force_reload:
            reset_collection(company_slug)

        texts = self._loader.load_csv(filepath)
        return self._store_documents(company_slug, texts, source=filepath, category="faq")

    def build_from_pdf(self, filepath: str, company_slug: str = "default") -> int:
        texts = self._loader.load_pdf(filepath)
        return self._store_documents(company_slug, texts, source=filepath, category="document")

    def build_from_dict(self, data: list, company_slug: str = "default") -> int:
        texts = self._loader.load_from_dict(data)
        return self._store_documents(company_slug, texts, source="dict_input", category="custom")
