# Multi-Tenant AI Customer Care Bot — Documentation

Complete documentation for the Multi-Tenant AI Customer Care Bot.

---

## Table of Contents

- [Architecture Overview](./architecture.md)
- **Backend**
  - [README](./backend/README.md) — tech stack, project structure, design decisions
  - [Setup Guide](./backend/setup.md) — local dev, env vars, model fallback chain
  - [API Reference](./backend/api.md) — all endpoints, request/response shapes
  - [Maintenance Guide](./backend/maintenance.md) — monitoring, quota, troubleshooting
- **Frontend**
  - [README](./frontend/README.md) — overview, tech stack
  - [Architecture](./frontend/architecture.md) — component tree, streaming flow, state
  - [Component Specification](./frontend/components.md) — props, behaviour, API client
  - [Integration Guide](./frontend/integration.md) — setup, customisation, deployment
- **Database**
  - [README](./database/README.md) — SQLite vs PostgreSQL, ChromaDB overview
  - [Schema](./database/schema.md) — tables, indexes, vector collection structure
  - [Security](./database/security.md) — API key hashing, PII redaction, isolation
  - [Backup & Recovery](./database/backup.md) — backup scripts, restore procedures

---

## Quick Start

### Backend
```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux
pip install -r requirements.txt
cp .env.example .env
# Edit .env — set GEMINI_API_KEY and GOOGLE_API_KEY
uvicorn main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

### Create demo company + load knowledge base
```bash
# 1. Create demo company (auto-generates API key)
curl -X POST http://localhost:8000/api/demo-company

# 2. Upload sample FAQs (use api_key from step 1)
curl -X POST http://localhost:8000/api/knowledge/upload-csv \
  -H "X-API-Key: <api_key>" \
  -F "file=@backend/data/sample_faqs.csv"
```

Open http://localhost:5173 — the chat widget connects to `demo-corp` by default.

---

## What Changed (Latest Updates)

| Area | Change |
|------|--------|
| Company creation | API key and slug are now **auto-generated** — no manual input needed |
| LLM | Uses **LangChain v2** (`langchain-google-genai==2.0.0`) |
| Model | Primary model changed to **`gemini-3.5-flash`** (separate quota pool) |
| Fallback chain | 5-model automatic fallback on 429 quota errors |
| Streaming | New `/api/chat/stream` SSE endpoint — tokens appear as they arrive |
| Frontend | `sendMessageStream()` with live token rendering and blinking cursor |
| Escalation | LLM failures no longer trigger escalation (only real LLM responses do) |
