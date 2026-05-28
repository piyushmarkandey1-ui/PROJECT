import logging
from typing import List, Optional

from pydantic import BaseModel

from database import chromadb_client

logger = logging.getLogger(__name__)


class RetrievedDoc(BaseModel):
    text: str
    score: float
    metadata: dict
    source: str


class Retriever:
    # Cosine similarity thresholds (ChromaDB returns distance, we convert)
    MIN_SCORE: float = 0.30       # filter out very weak matches
    RELEVANCE_THRESHOLD: float = 0.25  # is_relevant() gate

    def _distance_to_score(self, distance: float) -> float:
        """Convert ChromaDB cosine distance → similarity score.

        ChromaDB with hnsw:space=cosine returns distances in [0, 2].
        similarity = 1 - (distance / 2)  →  range [0, 1]
        """
        return round(max(0.0, 1.0 - (distance / 2.0)), 4)

    def retrieve(self, query: str, company_slug: str = "default", n_results: int = 3) -> List[RetrievedDoc]:
        try:
            collection = chromadb_client.get_collection(company_slug)
            count = collection.count()
            if count == 0:
                logger.warning("Knowledge base for company '%s' is empty — no retrieval possible", company_slug)
                return []

            results = collection.query(
                query_texts=[query],
                n_results=min(n_results, count),
                include=["documents", "metadatas", "distances"],
            )

            documents = results.get("documents", [[]])[0]
            metadatas = results.get("metadatas", [[]])[0]
            distances = results.get("distances", [[]])[0]

            docs: List[RetrievedDoc] = []
            for text, meta, dist in zip(documents, metadatas, distances):
                score = self._distance_to_score(dist)
                if score >= self.MIN_SCORE:
                    docs.append(
                        RetrievedDoc(
                            text=text,
                            score=score,
                            metadata=meta or {},
                            source=(meta or {}).get("source", "unknown"),
                        )
                    )

            logger.info(
                "Retrieved %d relevant docs (from %d candidates) for company '%s' and query: %s",
                len(docs),
                len(documents),
                company_slug,
                query[:60],
            )
            return docs

        except Exception as e:
            logger.error("Retrieval failed for company '%s': %s", company_slug, e)
            return []

    def format_context(self, docs: List[RetrievedDoc]) -> str:
        if not docs:
            return ""
        lines = [
            "Knowledge context (highest relevance first). Use this to answer precisely:",
            "If the context does not cover the user's exact question, explicitly say what is missing.",
        ]
        for i, doc in enumerate(docs, 1):
            lines.append(
                f"\n[{i}] Source: {doc.source} | Relevance: {doc.score:.2f}\n{doc.text}"
            )
        return "\n".join(lines)

    def is_relevant(self, query: str, company_slug: str = "default") -> bool:
        try:
            collection = chromadb_client.get_collection(company_slug)
            if collection.count() == 0:
                return False
            results = collection.query(
                query_texts=[query],
                n_results=1,
                include=["distances"],
            )
            distances = results.get("distances", [[]])[0]
            if not distances:
                return False
            score = self._distance_to_score(distances[0])
            logger.debug("Relevance score for company '%s' and query '%s': %.4f", company_slug, query[:60], score)
            return score >= self.RELEVANCE_THRESHOLD
        except Exception as e:
            logger.error("Relevance check failed for company '%s': %s", company_slug, e)
            return False
