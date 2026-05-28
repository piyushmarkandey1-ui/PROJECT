# Database Documentation

## Overview

The system uses two persistence layers:

1. **SQL Database** (SQLite / PostgreSQL) — company profiles, hashed API keys
2. **Vector Database** (ChromaDB) — per-company knowledge base embeddings

## Table of Contents

- [Schema](./schema.md)
- [Security](./security.md)
- [Backup & Recovery](./backup.md)

---

## Database Selection

### Development: SQLite (default)
- Company profiles stored at `COMPANY_DATABASE_URL` (default: `./companies.db`)
- File-based, zero configuration
- Auto-created on first startup
- Not suitable for multi-worker deployments

### Production: PostgreSQL
- Set `COMPANY_DATABASE_URL=postgresql://user:pass@host:5432/db` in `.env`
- Tables auto-created by SQLAlchemy on startup
- Required for Railway multi-instance deployments

---

## ChromaDB

- Persistent storage at `./chromadb_store` (configurable via `CHROMA_PERSIST_PATH`)
- Each company gets its own isolated collection: `kb_{company_slug}`
- Embedding model: `all-MiniLM-L6-v2` (384-dimensional, built into ChromaDB)
- Similarity metric: cosine distance (`hnsw:space=cosine`)
- Documents stored as `Q: {question}\nA: {answer}` strings

---

## Key Design Points

- **API keys are never stored in plaintext** — only SHA-256 hashes
- **Company isolation** — ChromaDB collections and sessions are keyed by company slug
- **Auto-slug generation** — slugs are derived from company name, with timestamp suffix on collision
- **Retry logic** — `KnowledgeBaseBuilder` retries ChromaDB writes up to 3 times with exponential backoff
