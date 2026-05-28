# Backend Setup Guide

## Prerequisites

- Python 3.11+
- pip
- Git
- A Google Gemini API key — get one free at [aistudio.google.com](https://aistudio.google.com)

---

## Local Development Setup

### 1. Clone & enter the backend directory
```bash
git clone <repository-url>
cd PROJECT/backend
```

### 2. Create and activate a virtual environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment variables
```bash
cp .env.example .env
```

Edit `.env`:
```env
GEMINI_API_KEY=your-gemini-api-key-here
GOOGLE_API_KEY=your-gemini-api-key-here   # same key — LangChain reads this
LLM_MODEL=gemini-3.5-flash
LLM_FALLBACK_MODELS=gemini-3.1-flash-lite,gemini-3-flash-preview,gemini-2.0-flash,gemini-2.0-flash-lite
COMPANY_DATABASE_URL=sqlite:///./companies.db
CHROMA_PERSIST_PATH=./chromadb_store
SECRET_KEY=your-secret-key-here
PORT=8000
MAX_TOKENS=1024
```

### 5. Start the server
```bash
uvicorn main:app --reload --port 8000
```

API available at: http://localhost:8000  
Interactive docs: http://localhost:8000/docs

### 6. Create a demo company and load sample data
```bash
# Create demo company (auto-generates API key)
curl -X POST http://localhost:8000/api/demo-company

# Note the api_key from the response, then upload FAQs:
curl -X POST http://localhost:8000/api/knowledge/upload-csv \
  -H "X-API-Key: <api_key_from_above>" \
  -F "file=@data/sample_faqs.csv"
```

---

## Environment Variables Reference

| Variable | Description | Default |
|----------|-------------|---------|
| `GEMINI_API_KEY` | Google Gemini API key | **Required** |
| `GOOGLE_API_KEY` | Same key — used by LangChain | **Required** |
| `LLM_MODEL` | Primary Gemini model | `gemini-3.5-flash` |
| `LLM_FALLBACK_MODELS` | Comma-separated fallback models tried on 429 | `gemini-3.1-flash-lite,...` |
| `MAX_TOKENS` | Max tokens per LLM response | `1024` |
| `COMPANY_DATABASE_URL` | SQL connection string for company profiles | `sqlite:///./companies.db` |
| `CHROMA_PERSIST_PATH` | ChromaDB storage directory | `./chromadb_store` |
| `SECRET_KEY` | App secret key | `changeme` |
| `CONFIDENCE_THRESHOLD` | Escalation confidence threshold | `0.70` |
| `PORT` | Server port | `8000` |

---

## Model Fallback Chain

The system automatically tries models in order when quota is exhausted (HTTP 429):

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

Free tier limits (as of 2026):
- `gemini-3.5-flash`: ~1500 RPD, 15 RPM
- `gemini-2.0-flash-lite`: 1500 RPD, 30 RPM
- `gemini-2.5-flash`: 250 RPD, 10 RPM (avoid as primary)

---

## Production Setup (Railway)

### 1. Install Railway CLI
```bash
npm install -g @railway/cli
```

### 2. Login and initialise
```bash
railway login
cd backend
railway init
```

### 3. Set environment variables
```bash
railway variables set GEMINI_API_KEY=your-key
railway variables set GOOGLE_API_KEY=your-key
railway variables set LLM_MODEL=gemini-3.5-flash
railway variables set COMPANY_DATABASE_URL=postgresql://user:pass@host:5432/db
railway variables set SECRET_KEY=your-production-secret
```

### 4. Deploy
```bash
railway up
```

---

## Database Configuration

### SQLite (Development — default)
```env
COMPANY_DATABASE_URL=sqlite:///./companies.db
```

### PostgreSQL (Production)
```env
DATABASE_URL=postgresql://username:password@hostname:5432/database_name
```

Tables are auto-created on startup via SQLAlchemy — no migration needed for fresh installs.

---

## Running Tests

```bash
cd backend
python test_bot.py
```

The test script:
1. Seeds the knowledge base with `data/sample_faqs.csv`
2. Runs 5 test messages through the full pipeline
3. Reports confidence, escalation, and pass/fail per message
