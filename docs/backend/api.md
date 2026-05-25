# API Reference

## Base URL

**Local:** `http://localhost:8000/api`  
**Production:** `https://your-backend-url.railway.app/api`

## Authentication

Protected endpoints require an API key via the `X-API-Key` header.  
The API key is returned **once** when a company is created — store it securely.

```bash
curl -X POST http://localhost:8000/api/knowledge/upload-csv \
  -H "X-API-Key: EDagr3SMHDxrfTXtjyYOotqHvgvHhuxG" \
  -F "file=@faqs.csv"
```

---

## Company Management

### Create Company
API key and slug are **auto-generated** — you do not need to provide them.

```http
POST /api/companies
Content-Type: application/json

{
  "name": "Acme Corp",
  "email": "support@acme.com",
  "contact_phone": "555-1234",
  "slug": "acme-corp"   ← optional, auto-generated from name if omitted
}
```

**Response (201):**
```json
{
  "id": "b6c5a0b9-9b5b-4a97-a445-826555d92b9b",
  "name": "Acme Corp",
  "slug": "acme-corp",
  "email": "support@acme.com",
  "contact_phone": "555-1234",
  "api_key": "EDagr3SMHDxrfTXtjyYOotqHvgvHhuxG",  ← shown ONCE only
  "created_at": "2026-05-25T10:00:00Z",
  "updated_at": "2026-05-25T10:00:00Z"
}
```

> ⚠️ **Save the `api_key` immediately.** It is hashed and stored — the plaintext is never shown again.

---

### Create Demo Company
Creates (or resets) a pre-configured demo company for testing.

```http
POST /api/demo-company
```

**Response (201):** Same as Create Company with `slug: "demo-corp"`.

---

### Get Company by Slug
```http
GET /api/companies/{slug}
```

**Response (200):**
```json
{
  "id": "uuid",
  "name": "Acme Corp",
  "slug": "acme-corp",
  "email": "support@acme.com",
  "contact_phone": "555-1234",
  "created_at": "2026-05-25T10:00:00Z",
  "updated_at": "2026-05-25T10:00:00Z"
}
```

---

### List All Companies
```http
GET /api/companies
```

**Response (200):**
```json
{
  "companies": [...],
  "count": 3
}
```

---

### Update Company
```http
PUT /api/companies/{slug}
X-API-Key: your-api-key
Content-Type: application/json

{
  "name": "New Name",
  "email": "new@email.com",
  "contact_phone": "555-9999"
}
```

> Only the company's own API key can update its profile.

---

### Delete Company
```http
DELETE /api/companies/{slug}
X-API-Key: your-api-key
```

> Deletes the company profile and its ChromaDB knowledge base collection.

---

## Chat

### Send Message (Full Response)
Returns the complete response after the LLM finishes.

```http
POST /api/chat
Content-Type: application/json

{
  "session_id": null,
  "message": "How do I track my order?",
  "company_slug": "acme-corp"
}
```

**Response (200):**
```json
{
  "session_id": "910103df-2a47-4f7f-b6a5-7876935268fe",
  "response": "Once your order ships, you'll receive a tracking number via email...",
  "confidence": 0.85,
  "is_escalated": false,
  "escalation_reason": null,
  "retrieved_sources": ["sample_faqs.csv"],
  "turn_count": 2,
  "timestamp": "2026-05-25T10:00:00Z"
}
```

| Field | Description |
|-------|-------------|
| `confidence` | `0.85` = relevant KB docs found; `0.55` = no relevant docs |
| `is_escalated` | `true` if escalation was triggered |
| `escalation_reason` | Why escalation was triggered (if applicable) |
| `retrieved_sources` | Which knowledge base files were used |

---

### Send Message (Streaming SSE)
Streams tokens as they arrive via Server-Sent Events. Much faster perceived response.

```http
POST /api/chat/stream
Content-Type: application/json

{
  "session_id": null,
  "message": "What is your return policy?",
  "company_slug": "acme-corp"
}
```

**Response:** `text/event-stream`

```
data: {"token": "We"}

data: {"token": " accept"}

data: {"token": " returns"}

data: {"token": " within"}

data: {"token": " 30 days..."}

data: {"done": true, "session_id": "uuid", "confidence": 0.85, "sources": ["faqs.csv"], "turn_count": 2}
```

**Special events:**
- `{"reset": true}` — model switched mid-stream (quota fallback), clear accumulated tokens
- `{"token": "...", "error": true}` — all models rate-limited

---

## Session Management

### Create New Session
```http
POST /api/session/new?company_slug=acme-corp
```

**Response (200):**
```json
{
  "session_id": "uuid",
  "created_at": "2026-05-25T10:00:00Z"
}
```

---

### Get Session History
```http
GET /api/session/{company_slug}/{session_id}/history
```

**Response (200):**
```json
{
  "session_id": "uuid",
  "messages": [
    {"role": "user", "content": "Hello"},
    {"role": "assistant", "content": "Hi! How can I help?"}
  ],
  "count": 2
}
```

---

### Clear Session
```http
DELETE /api/session/{company_slug}/{session_id}
```

---

## Knowledge Base

### Upload CSV
```http
POST /api/knowledge/upload-csv
X-API-Key: your-api-key
Content-Type: multipart/form-data

file: your-faqs.csv
```

**CSV Format:**
```csv
question,answer,category
How do I track my order?,Once your order ships you will receive a tracking number via email.,shipping
What is your return policy?,We accept returns within 30 days of delivery.,returns
```

> Fields with commas must be quoted: `"We accept Visa, Mastercard, and PayPal."`

**Response (200):**
```json
{
  "message": "Successfully added 20 documents to Acme Corp's knowledge base",
  "documents_added": 20
}
```

---

### Knowledge Base Stats
```http
GET /api/knowledge/stats
X-API-Key: your-api-key
```

Or with query param (no auth needed):
```http
GET /api/knowledge/stats?company_slug=acme-corp
```

**Response (200):**
```json
{
  "total_documents": 20,
  "status": "ready"
}
```

---

## Health Check

```http
GET /api/health
```

**Response (200):**
```json
{
  "status": "healthy",
  "timestamp": "2026-05-25T10:00:00Z",
  "model": "gemini-3.5-flash",
  "knowledge_base_docs": 0
}
```

---

## Error Responses

| Status | Meaning |
|--------|---------|
| `400` | Bad request (validation error, duplicate slug) |
| `401` | Missing or invalid `X-API-Key` |
| `403` | API key valid but wrong company (e.g., updating another company) |
| `404` | Company or session not found |
| `500` | Internal server error |

**Error body:**
```json
{
  "detail": "Company not found"
}
```
