# Backend Maintenance Guide

## Monitoring

### Health Check
```bash
curl http://localhost:8000/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "model": "gemini-3.5-flash",
  "timestamp": "2026-05-25T10:00:00Z",
  "knowledge_base_docs": 0
}
```

### Logs
Logs are written to stdout in the format:
```
2026-05-25 10:00:00,000 [INFO] services.chatservice.handler: Gemini OK (model=gemini-3.5-flash, chars=245)
2026-05-25 10:00:00,000 [WARNING] services.chatservice.handler: Quota hit on gemini-3.5-flash, trying next model...
2026-05-25 10:00:00,000 [INFO] services.chatservice.handler: Gemini OK (model=gemini-3.1-flash-lite, chars=245)
```

Key log patterns to watch:
- `Gemini OK` — successful LLM response
- `Quota hit on ... trying next model` — fallback chain activated
- `All models failed` — all 5 models exhausted (very rare)
- `Escalation triggered` — customer escalated to human agent

---

## Gemini Quota Management

The system uses a 5-model fallback chain. If you see frequent "All models failed" errors:

1. Check quota usage at [ai.dev/rate-limit](https://ai.dev/rate-limit)
2. Add billing to your Google AI Studio account for higher limits
3. Adjust `LLM_FALLBACK_MODELS` in `.env` to add more models

Free tier limits (2026):
| Model | RPD | RPM |
|-------|-----|-----|
| gemini-3.5-flash | ~1500 | 15 |
| gemini-3.1-flash-lite | ~1500 | 15 |
| gemini-2.0-flash-lite | 1500 | 30 |
| gemini-2.0-flash | 200 | 15 |
| gemini-2.5-flash | 250 | 10 |

---

## Backups

### SQLite Database
```bash
# Backup
cp customer_care_bot.db customer_care_bot.backup.$(date +%Y%m%d).db

# Restore
cp customer_care_bot.backup.20260525.db customer_care_bot.db
```

### PostgreSQL
```bash
# Backup
pg_dump -U username -h hostname database_name > backup_$(date +%Y%m%d).sql

# Restore
psql -U username -h hostname database_name < backup_20260525.sql
```

### ChromaDB
```bash
# Backup
tar -czf chromadb_backup_$(date +%Y%m%d).tar.gz ./chromadb_store

# Restore
tar -xzf chromadb_backup_20260525.tar.gz
```

---

## Updating

### Deploying Code Updates
```bash
cd backend
git pull origin main
pip install -r requirements.txt
# Restart uvicorn (or Railway auto-deploys on push)
```

### Updating LangChain
```bash
pip install --upgrade langchain-google-genai langchain-core
```

> After upgrading, verify `chunk.content` format hasn't changed — in v4 it's `list[dict]`.  
> The `_extract_chunk_text()` helper in `handler.py` handles both `str` and `list[dict]`.

### Database Migrations
For schema changes in production, use Alembic:
```bash
alembic revision --autogenerate -m "add new column"
alembic upgrade head
```

---

## Troubleshooting

### "All models failed" / constant rate-limit errors
- All 5 models in the fallback chain hit their daily quota
- Wait until midnight Pacific time (quotas reset daily)
- Or add billing at [aistudio.google.com](https://aistudio.google.com)

### "sequence item 0: expected str instance, list found"
- LangChain can return `chunk.content` as either `str` or `list[dict]`
- Fix: ensure `_extract_chunk_text()` is used in `handler.py` and `router.py`

### ChromaDB initialization failed
```bash
# Delete corrupted store and restart
rm -rf ./chromadb_store
uvicorn main:app --reload
# Then re-upload knowledge base CSVs
```

### Company slug collision
- Slugs are auto-generated from company name
- If a collision occurs, a timestamp suffix is appended automatically
- You can also provide a custom slug in the request body

### Session not found (404)
- Sessions expire after 30 minutes of inactivity
- The frontend auto-creates a new session on the next message
- Session history is in-memory — it does not survive server restarts

### CORS errors in browser
- Development: CORS is wide-open (`allow_origins=["*"]`)
- Production: set `FRONTEND_URL` in `.env` and restrict `allow_origins` in `main.py`

---

## Performance Optimization

### Reduce LLM Latency
- Use streaming (`/api/chat/stream`) — users see tokens immediately
- Lower `MAX_TOKENS` in `.env` (currently 1024) for faster responses
- `gemini-2.0-flash-lite` is the fastest model in the fallback chain

### ChromaDB Query Speed
- Keep knowledge bases under 10,000 documents per company
- Use specific, well-formatted Q&A pairs in CSVs
- The retriever fetches top-3 docs — adjust `n_results` in `retriever.py` if needed

### Session Memory
- Sessions are in-memory — they don't survive restarts
- For production persistence, replace `SessionManager` with Redis
- Current limits: 30-min TTL, 50 messages max per session

### Scaling
```bash
# Multiple workers (requires PostgreSQL, not SQLite)
uvicorn main:app --workers 4 --host 0.0.0.0 --port 8000
```
