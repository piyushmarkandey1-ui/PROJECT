# 🤖 Multi-Tenant AI Customer Care Bot

![Python](https://img.shields.io/badge/Python-3.11+-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green)
![React](https://img.shields.io/badge/React-18-61DAFB)
![LangChain](https://img.shields.io/badge/LangChain-4.x-yellow)
![ChromaDB](https://img.shields.io/badge/ChromaDB-0.5-orange)
![Gemini](https://img.shields.io/badge/Gemini-3.5--flash-purple)

A production-grade, multi-tenant AI customer care chatbot built on a **Retrieval-Augmented Generation (RAG)** architecture. Each company gets its own isolated knowledge base, auto-generated API key, and session space. The system uses **LangChain + Google Gemini** with an automatic **5-model fallback chain**, **streaming responses via SSE**, ChromaDB for semantic search, emotional intelligence for escalation, and PII guardrails.

---

## Architecture

```
User (React Frontend — SSE streaming)
        │
        ▼
FastAPI Backend
  ├── GuardrailsEngine     — topic filter + PII sanitization
  ├── SessionManager       — in-memory, company-isolated (30-min TTL)
  ├── Retriever            — ChromaDB cosine-similarity RAG (top-3 docs)
  ├── ChatHandler          — LangChain + Gemini with 5-model fallback
  │     └── Model chain:  gemini-3.5-flash → gemini-3.1-flash-lite
  │                        → gemini-3-flash-preview → gemini-2.0-flash
  │                        → gemini-2.0-flash-lite
  └── EscalationEngine     — sentiment + urgency + intensity analysis
        │
        ▼
ChromaDB (Vector Store)  ←  KnowledgeBaseBuilder (CSV / PDF)
SQLite / PostgreSQL      ←  Company profiles + hashed API keys
```

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| LLM | Google Gemini (`gemini-3.5-flash` primary, 4-model fallback) |
| LLM Framework | LangChain Google GenAI (`langchain-google-genai==2.0.0`) |
| Streaming | Server-Sent Events (SSE) via FastAPI `StreamingResponse` |
| Embeddings | ChromaDB built-in (`all-MiniLM-L6-v2`, 384-dim) |
| Vector DB | ChromaDB 0.5 (persistent, per-company collections) |
| Backend | FastAPI 0.115 + Uvicorn |
| Frontend | React 18 + Vite + Tailwind CSS |
| SQL DB | SQLite (dev) / PostgreSQL (prod) |
| ORM | SQLAlchemy 2.0 |
| Deploy (BE) | Railway |
| Deploy (FE) | Vercel |

---

## Key Features

| Feature | Detail |
|---------|--------|
| **Multi-tenancy** | Isolated ChromaDB collection, sessions, and API key per company |
| **Auto API key generation** | 32-char cryptographically secure key, SHA-256 hashed in DB |
| **Auto slug generation** | Derived from company name, timestamp suffix on collision |
| **Streaming responses** | Tokens stream to browser via SSE — instant perceived response |
| **5-model fallback chain** | Auto-switches models on 429 quota errors, no user-visible error |
| **RAG** | Cosine-similarity retrieval from company-specific knowledge base |
| **Emotional intelligence** | Sentiment + urgency + intensity → smart escalation decisions |
| **PII guardrails** | Credit card, SSN, password patterns auto-redacted in responses |
| **Session isolation** | 30-min TTL, 50-msg cap, company-scoped |

---

## Quick Start

### 1. Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux

pip install -r requirements.txt
cp .env.example .env
# Edit .env — set GEMINI_API_KEY and GOOGLE_API_KEY to the same key
uvicorn main:app --reload --port 8000
```

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173

### 3. Create a company and load knowledge base

```bash
# Create demo company (auto-generates API key + slug)
curl -X POST http://localhost:8000/api/demo-company

# Or create your own company (slug is optional — auto-generated from name)
curl -X POST http://localhost:8000/api/companies \
  -H "Content-Type: application/json" \
  -d '{"name":"Acme Corp","email":"support@acme.com"}'

# Upload FAQ CSV (use the api_key from the response above)
curl -X POST http://localhost:8000/api/knowledge/upload-csv \
  -H "X-API-Key: <your-api-key>" \
  -F "file=@backend/data/sample_faqs.csv"
```

---

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `GEMINI_API_KEY` | Google Gemini API key | **Required** |
| `GOOGLE_API_KEY` | Same key — LangChain reads this | **Required** |
| `LLM_MODEL` | Primary Gemini model | `gemini-3.5-flash` |
| `LLM_FALLBACK_MODELS` | Comma-separated fallback models | `gemini-3.1-flash-lite,...` |
| `MAX_TOKENS` | Max tokens per LLM response | `1024` |
| `DATABASE_URL` | SQL connection string | `sqlite:///./customer_care_bot.db` |
| `CHROMA_PERSIST_PATH` | ChromaDB storage path | `./chromadb_store` |
| `CONFIDENCE_THRESHOLD` | Escalation confidence threshold | `0.70` |
| `PORT` | Server port | `8000` |

---

## API Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `POST` | `/api/companies` | — | Create company (returns API key once) |
| `GET` | `/api/companies` | — | List all companies |
| `GET` | `/api/companies/{slug}` | — | Get company by slug |
| `PUT` | `/api/companies/{slug}` | API Key | Update company |
| `DELETE` | `/api/companies/{slug}` | API Key | Delete company + KB |
| `POST` | `/api/demo-company` | — | Create/reset demo company |
| `POST` | `/api/chat` | — | Send message, get full JSON response |
| `POST` | `/api/chat/stream` | — | Send message, stream tokens via SSE |
| `POST` | `/api/session/new` | — | Create new session |
| `GET` | `/api/session/{slug}/{id}/history` | — | Get session history |
| `DELETE` | `/api/session/{slug}/{id}` | — | Clear session |
| `POST` | `/api/knowledge/upload-csv` | API Key | Upload FAQ CSV |
| `GET` | `/api/knowledge/stats` | API Key | Knowledge base stats |
| `GET` | `/api/health` | — | Health check |

---

## Model Fallback Chain

Automatically tries models in order when quota is hit (HTTP 429):

```
gemini-3.5-flash          ← primary (separate quota from 2.x models)
  ↓ quota hit
gemini-3.1-flash-lite     ← fallback 1
  ↓ quota hit
gemini-3-flash-preview    ← fallback 2
  ↓ quota hit
gemini-2.0-flash          ← fallback 3
  ↓ quota hit
gemini-2.0-flash-lite     ← fallback 4
```

Free tier limits (2026): `gemini-3.5-flash` and `gemini-2.0-flash-lite` both offer ~1500 RPD.

---

## Deploy

### Backend → Railway

```bash
cd backend
railway login
railway init
railway variables set GEMINI_API_KEY=your-key
railway variables set GOOGLE_API_KEY=your-key
railway variables set LLM_MODEL=gemini-3.5-flash
railway up
```

### Frontend → Vercel

```bash
cd frontend
npm run build
vercel --prod
# Set VITE_API_URL to your Railway backend URL in Vercel dashboard
```

---

## Running Tests

```bash
cd backend
python test_bot.py
```

---

## Documentation

Full documentation is in the [`docs/`](./docs/) directory:

- [Architecture](./docs/architecture.md)
- [Backend Setup](./docs/backend/setup.md)
- [API Reference](./docs/backend/api.md)
- [Frontend Architecture](./docs/frontend/architecture.md)
- [Database Schema](./docs/database/schema.md)
