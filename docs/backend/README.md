# Backend Documentation

## Overview

The backend is a FastAPI application providing a multi-tenant AI customer care API. It uses LangChain with Google Gemini for LLM responses, ChromaDB for vector search (RAG), and SQLite/PostgreSQL for company profiles.

## Table of Contents

- [Setup Guide](./setup.md)
- [API Reference](./api.md)
- [Maintenance Guide](./maintenance.md)

---

## Tech Stack

| Layer | Technology | Version |
|-------|-----------|---------|
| Framework | FastAPI + Uvicorn | 0.115 |
| LLM Framework | LangChain Google GenAI | 2.0.0 |
| LLM | Google Gemini (5-model fallback chain) | gemini-3.5-flash primary |
| Streaming | FastAPI `StreamingResponse` (SSE) | — |
| Vector DB | ChromaDB (persistent, per-company) | 0.5 |
| Embeddings | all-MiniLM-L6-v2 (built into ChromaDB) | 384-dim |
| SQL ORM | SQLAlchemy | 2.0 |
| SQL DB | SQLite (dev) / PostgreSQL (prod) | — |
| Validation | Pydantic | 2.x |

---

## Project Structure

```
backend/
├── main.py                          # FastAPI app, lifespan, CORS
├── .env                             # Environment variables (not committed)
├── .env.example                     # Template for .env
├── requirements.txt
├── core/
│   ├── config.py                    # Settings (pydantic-settings, lru_cache)
│   ├── auth.py                      # X-API-Key dependency
│   └── guardrails.py                # Topic filter + PII sanitization
├── database/
│   ├── db.py                        # SQLAlchemy engine + session factory
│   ├── models.py                    # Company ORM model
│   ├── company_store.py             # CRUD + auto API key/slug generation
│   └── chromadb_client.py           # ChromaDB client + collection management
├── models/
│   └── schemas.py                   # Pydantic request/response schemas
├── services/
│   ├── chatservice/
│   │   ├── handler.py               # ChatHandler — LangChain + fallback chain
│   │   └── router.py                # /chat, /chat/stream, company, session, KB endpoints
│   ├── ragservice/
│   │   ├── embedder.py              # KnowledgeBaseBuilder (CSV/PDF → ChromaDB)
│   │   ├── loader.py                # DocumentLoader (CSV, PDF, text, dict)
│   │   └── retriever.py             # Cosine-similarity retrieval + relevance check
│   ├── sessionservice/
│   │   └── memory.py                # In-memory session manager (company-isolated)
│   └── escalationservice/
│       └── trigger.py               # EscalationEngine (sentiment + urgency)
└── data/
    ├── sample_faqs.csv              # Demo knowledge base
    ├── acme_corp_faqs.csv
    └── techsolutions_faqs.csv
```

---

## Key Design Decisions

### Auto API Key Generation
Companies no longer need to provide an API key. On creation:
- A 32-character cryptographically secure key is generated via `secrets.choice()`
- The SHA-256 hash is stored — plaintext is returned once and never stored
- Slug is auto-generated from the company name if not provided

### LangChain + Streaming
- `ChatGoogleGenerativeAI(streaming=True)` with `astream()` for token-by-token delivery
- `chunk.content` in LangChain v4 is `list[dict]` — extracted via `_extract_chunk_text()`
- Frontend receives tokens via SSE (`text/event-stream`) for instant perceived response

### Model Fallback Chain
When a model returns HTTP 429 (quota exhausted), the handler automatically tries the next model in the chain without the user seeing an error.

### Session Isolation
Sessions are keyed by `(company_slug, session_id)` — a session from company A cannot be accessed by company B even if the session ID is known.
