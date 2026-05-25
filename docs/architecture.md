# Architecture Overview

## System Architecture

```
┌──────────────────────────────────────────────────────────────────────────┐
│                     Frontend (React 18 + Vite + Tailwind)                │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────────┐  │
│  │   ChatWidget     │  │  MessageBubble   │  │  EscalationAlert     │  │
│  │  (SSE streaming) │  │ (streaming cursor)│  │  (yellow banner)     │  │
│  └──────────────────┘  └──────────────────┘  └──────────────────────┘  │
└──────────────────────────────────────────────────────────────────────────┘
                                      │  SSE / JSON
                                      ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                      FastAPI Backend (Python 3.11+)                      │
│  ┌────────────────────────────────────────────────────────────────────┐  │
│  │  API Layer — /api/*                                                │  │
│  ├────────────────────────────────────────────────────────────────────┤  │
│  │  Auth (X-API-Key)  │  Company CRUD  │  Chat  │  Chat/Stream (SSE) │  │
│  ├────────────────────────────────────────────────────────────────────┤  │
│  │  GuardrailsEngine  │  SessionManager  │  EscalationEngine         │  │
│  ├────────────────────────────────────────────────────────────────────┤  │
│  │                    ChatHandler (LangChain)                         │  │
│  │   Model chain: gemini-3.5-flash → gemini-3.1-flash-lite           │  │
│  │                → gemini-3-flash-preview → gemini-2.0-flash        │  │
│  │                → gemini-2.0-flash-lite  (auto-fallback on 429)    │  │
│  ├────────────────────────────────────────────────────────────────────┤  │
│  │                    RAG Service Layer                               │  │
│  │  ┌──────────────────┐  ┌──────────────────┐  ┌────────────────┐  │  │
│  │  │  DocumentLoader  │  │  KnowledgeBase   │  │   Retriever    │  │  │
│  │  │  (CSV / PDF)     │  │  Builder         │  │  (cosine sim)  │  │  │
│  │  └──────────────────┘  └──────────────────┘  └────────────────┘  │  │
│  └────────────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────────────┘
                  │                                       │
     ┌────────────▼────────────┐           ┌─────────────▼─────────────┐
     │  SQL Database           │           │  ChromaDB (Vector Store)  │
     │  SQLite / PostgreSQL    │           │  Per-company collections  │
     │  ┌─────────────────┐   │           │  ┌─────────────────────┐  │
     │  │ companies table │   │           │  │ kb_<company-slug>   │  │
     │  │ (profiles +     │   │           │  │ (384-dim embeddings)│  │
     │  │  hashed keys)   │   │           │  └─────────────────────┘  │
     │  └─────────────────┘   │           └───────────────────────────┘
     └─────────────────────────┘
```

---

## Key Components

### 1. Frontend (React 18)

| Component | Purpose |
|-----------|---------|
| `ChatWidget` | Main chat UI — manages streaming state, session, escalation |
| `MessageBubble` | Renders user/bot messages with live streaming cursor |
| `TypingIndicator` | Animated dots shown before first token arrives |
| `EscalationAlert` | Yellow banner when human agent is being connected |
| `api.js` | `sendMessageStream()` reads SSE chunks; `sendMessage()` for non-streaming |

### 2. Backend (FastAPI)

| Module | Purpose |
|--------|---------|
| `ChatHandler` | Orchestrates full pipeline: guardrails → RAG → LangChain → escalation |
| `GuardrailsEngine` | Off-topic detection + PII redaction (CC, SSN, passwords) |
| `SessionManager` | In-memory, company-isolated sessions (30-min TTL, 50-msg cap) |
| `Retriever` | ChromaDB cosine-similarity search with score threshold |
| `KnowledgeBaseBuilder` | Ingests CSV/PDF into ChromaDB with retry logic |
| `EscalationEngine` | Sentiment + urgency + intensity analysis → escalation decision |

### 3. LLM Layer (LangChain + Gemini)

- Uses `langchain-google-genai==2.0.0` with `ChatGoogleGenerativeAI`
- `streaming=True` enables token-by-token delivery via `astream()`
- `chunk.content` can be either `str` or `list[dict]` — extracted with `_extract_chunk_text()`
- **Fallback chain**: automatically tries 5 models on 429/quota errors

### 4. Databases

#### SQL (SQLite / PostgreSQL)
- Stores company profiles and SHA-256 hashed API keys
- Auto-creates tables on startup via SQLAlchemy

#### Vector (ChromaDB)
- Each company → isolated collection `kb_{slug}`
- `hnsw:space=cosine` for similarity search
- Embeddings: `all-MiniLM-L6-v2` (384-dim, built into ChromaDB)

---

## Data Flow

### Chat Flow (Streaming)
```
1. POST /api/chat/stream  { message, company_slug, session_id }
2. GuardrailsEngine.is_on_topic()  →  off-topic? return early
3. SessionManager.get_session_summary()  →  conversation context
4. Retriever.retrieve()  →  top-3 ChromaDB docs (cosine similarity)
5. Build system prompt = guardrails + RAG context + session history
6. LangChain astream() → try gemini-3.5-flash first
   └── 429? → try gemini-3.1-flash-lite → ... → gemini-2.0-flash-lite
7. Tokens stream to frontend via SSE as they arrive
8. EscalationEngine.should_escalate()  →  override response if needed
9. GuardrailsEngine.sanitize_response()  →  redact PII
10. SessionManager.add_message()  →  persist to session
11. SSE done event  →  { session_id, confidence, sources, turn_count }
```

### Company Registration Flow
```
1. POST /api/companies  { name, email, contact_phone, slug? }
2. Auto-generate slug from name if not provided
3. Auto-generate 32-char secure API key
4. SHA-256 hash the API key → store hash only
5. Return { ...company, api_key }  ← shown ONCE, never again
```

### Knowledge Base Upload Flow
```
1. POST /api/knowledge/upload-csv  (X-API-Key header)
2. Authenticate company via hashed API key lookup
3. Save uploaded file to temp path
4. DocumentLoader.load_csv()  →  parse Q&A pairs
5. KnowledgeBaseBuilder.build_from_csv()  →  reset + re-embed
6. ChromaDB.add_documents()  →  store with retry (3 attempts)
7. Return { documents_added: N }
```

---

## Escalation Logic

The `EscalationEngine` triggers escalation on any of these conditions:

| Condition | Priority |
|-----------|----------|
| Extreme negative emotion (intensity > 0.8) + high urgency | HIGH |
| Negative sentiment + urgency after 2+ turns | HIGH |
| Bot confidence < 0.70 (no relevant KB docs) | MEDIUM |
| Very negative sentiment (intensity > 0.7) | HIGH |
| Conversation > 10 turns unresolved | MEDIUM |
| User explicitly requests human agent | HIGH |

---

## Security

- API keys stored as SHA-256 hashes only — plaintext never persisted
- API key returned only once at company creation
- Session isolation: company A cannot access company B's sessions
- PII redaction: credit cards, SSNs, passwords auto-redacted in responses
- CORS: wide-open for development; restrict `allow_origins` in production
