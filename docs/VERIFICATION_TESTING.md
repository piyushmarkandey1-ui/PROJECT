# Verification & Testing Guide

## 1. Environment Setup Verification

```bash
cd backend
python -c "
from core.config import get_settings
s = get_settings()
print('API Key set:', bool(s.GEMINI_API_KEY))
print('Primary model:', s.LLM_MODEL)
print('Fallback chain:', s.fallback_model_list)
"
```

Expected output:
```
API Key set: True
Primary model: gemini-3.5-flash
Fallback chain: ['gemini-3.1-flash-lite', 'gemini-3-flash-preview', 'gemini-2.0-flash', 'gemini-2.0-flash-lite']
```

---

## 2. Backend Health Check

```bash
curl http://localhost:8000/api/health
```

Expected:
```json
{"status": "healthy", "model": "gemini-3.5-flash", "timestamp": "..."}
```

---

## 3. Company Creation Test

```bash
# Create company — no api_key or slug needed
curl -X POST http://localhost:8000/api/companies \
  -H "Content-Type: application/json" \
  -d '{"name":"Test Corp","email":"test@test.com"}'
```

Expected: `201` with `api_key` field (32 chars), `slug` auto-generated as `test-corp`.

---

## 4. Knowledge Base Upload Test

```bash
# Use api_key from step 3
curl -X POST http://localhost:8000/api/knowledge/upload-csv \
  -H "X-API-Key: <api_key>" \
  -F "file=@backend/data/sample_faqs.csv"
```

Expected: `{"documents_added": 20, "message": "Successfully added 20 documents..."}`

---

## 5. Chat Test (Non-Streaming)

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"What is your return policy?","company_slug":"test-corp"}'
```

Expected:
```json
{
  "response": "We accept returns within 30 days...",
  "confidence": 0.85,
  "is_escalated": false,
  "retrieved_sources": ["...sample_faqs.csv..."]
}
```

---

## 6. Streaming Chat Test

```bash
curl -N -X POST http://localhost:8000/api/chat/stream \
  -H "Content-Type: application/json" \
  -d '{"message":"How do I track my order?","company_slug":"test-corp"}'
```

Expected: SSE stream of `data: {"token": "..."}` lines, ending with `data: {"done": true, ...}`.

---

## 7. Escalation Test

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"I am very angry! I want to speak to a human agent!","company_slug":"test-corp"}'
```

Expected: `"is_escalated": true`, response contains "specialist" or "connect you".

---

## 8. Model Fallback Test

To test the fallback chain, temporarily set `LLM_MODEL` to an exhausted model and verify the system falls back automatically. Check server logs for:
```
WARNING: Quota hit on gemini-3.5-flash, trying next model...
INFO: Gemini OK (model=gemini-3.1-flash-lite, chars=...)
```

---

## 9. End-to-End Test Script

```bash
cd backend
python test_bot.py
```

This runs 5 test messages through the full pipeline and reports:
- Pass/fail per message
- Average confidence
- Escalation count

---

## 10. Frontend Verification

Open http://localhost:5173 and verify:

| Check | Expected |
|-------|----------|
| Page loads | Chat widget visible |
| Send "Hello" | Response appears token-by-token (streaming cursor visible) |
| Send FAQ question | Response references knowledge base content |
| Send angry message | Yellow escalation banner appears |
| Click "New chat" | History cleared, fresh greeting shown |
| Server offline | Red error banner: "Could not reach the server" |

---

## Known Limitations

| Limitation | Detail |
|-----------|--------|
| Free tier quota | 20-1500 RPD depending on model; resets at midnight Pacific |
| In-memory sessions | Lost on server restart; no persistence across deployments |
| ChromaDB telemetry errors | `capture() takes 1 positional argument` — cosmetic, does not affect functionality |
| Single-process only | SQLite + in-memory sessions require single-worker deployment |
