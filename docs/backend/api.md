# API Reference

## Base URL

**Local:** `http://localhost:8000/api`
**Production:** `https://your-backend-url.railway.app/api`

## Authentication

Most endpoints require API key authentication via the `X-API-Key` header.

**Example:**
```bash
curl -X GET http://localhost:8000/api/companies \
  -H "X-API-Key: your-api-key-here"
```

---

## Company Management

### Create Company
```http
POST /api/companies
Content-Type: application/json

{
  "name": "Acme Corp",
  "slug": "acme-corp",
  "email": "support@acme.com",
  "contact_phone": "555-1234",
  "api_key": "your-32-character-api-key"
}
```

**Response:**
```json
{
  "id": "uuid",
  "name": "Acme Corp",
  "slug": "acme-corp",
  "email": "support@acme.com",
  "contact_phone": "555-1234",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

### Get Company by Slug
```http
GET /api/companies/{slug}
```

### List All Companies
```http
GET /api/companies
```

### Update Company
```http
PUT /api/companies/{slug}
X-API-Key: your-api-key
Content-Type: application/json

{
  "name": "New Company Name",
  "email": "new-email@company.com"
}
```

### Delete Company
```http
DELETE /api/companies/{slug}
X-API-Key: your-api-key
```

---

## Chat

### Send Chat Message
```http
POST /api/chat
Content-Type: application/json

{
  "session_id": "optional-session-id",
  "message": "How do I track my order?",
  "company_slug": "acme-corp"
}
```

**Response:**
```json
{
  "session_id": "session-uuid",
  "response": "You can track your order by...",
  "confidence": 0.85,
  "is_escalated": false,
  "retrieved_sources": ["sample_faqs.csv"],
  "turn_count": 1,
  "timestamp": "2024-01-01T00:00:00Z"
}
```

---

## Session Management

### Create New Session
```http
POST /api/session/new
```

### Get Session History
```http
GET /api/session/{session_id}/history
```

### Clear Session
```http
DELETE /api/session/{session_id}
```

---

## Knowledge Base

### Upload CSV Knowledge Base
```http
POST /api/knowledge/upload-csv
X-API-Key: your-api-key
Content-Type: multipart/form-data

file: your-faqs.csv
```

**CSV Format:**
```csv
question,answer,category
How do I track my order?,Visit Orders > Track Order,shipping
What's your return policy?,30-day returns,returns
```

**Response:**
```json
{
  "message": "Successfully added 21 documents to Acme Corp's knowledge base",
  "documents_added": 21
}
```

### Get Knowledge Base Stats
```http
GET /api/knowledge/stats?company_slug=acme-corp
```

**Response:**
```json
{
  "total_documents": 21,
  "status": "ready"
}
```

---

## Health Check

```http
GET /api/health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T00:00:00Z",
  "model": "gemini-2.0-flash",
  "knowledge_base_docs": 0
}
```
