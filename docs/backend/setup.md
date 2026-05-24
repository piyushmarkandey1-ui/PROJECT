# Backend Setup Guide

## Prerequisites

- Python 3.11+
- pip
- Git

## Local Development Setup

### 1. Clone the Repository
```bash
git clone <repository-url>
cd customer-care-bot/backend
```

### 2. Create Virtual Environment
```bash
python -m venv venv
```

### 3. Activate Virtual Environment

**Windows:**
```bash
venv\Scripts\activate
```

**Mac/Linux:**
```bash
source venv/bin/activate
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Configure Environment Variables
```bash
cp .env.example .env
```

Edit `.env` and set the following:
```env
GEMINI_API_KEY=your-gemini-api-key-here
DATABASE_URL=sqlite:///./customer_care_bot.db
CHROMA_PERSIST_PATH=./chromadb_store
SECRET_KEY=your-secret-key-here
PORT=8000
```

### 6. Run the Application
```bash
uvicorn main:app --reload
```

The API will be available at http://localhost:8000

Visit http://localhost:8000/docs for interactive API documentation.

## Production Setup (Railway)

### 1. Install Railway CLI
```bash
npm install -g @railway/cli
```

### 2. Login to Railway
```bash
railway login
```

### 3. Initialize Railway Project
```bash
cd backend
railway init
```

### 4. Set Environment Variables
```bash
railway variables set GEMINI_API_KEY=your-key
railway variables set DATABASE_URL=postgresql://user:pass@host:5432/db
railway variables set SECRET_KEY=your-secret-key
```

### 5. Deploy
```bash
railway up
```

## Database Configuration

### SQLite (Development)
Default configuration:
```env
DATABASE_URL=sqlite:///./customer_care_bot.db
```

### PostgreSQL (Production)
```env
DATABASE_URL=postgresql://username:password@hostname:5432/database_name
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `GEMINI_API_KEY` | Google Gemini API key | Required |
| `DATABASE_URL` | SQL database connection string | `sqlite:///./customer_care_bot.db` |
| `CHROMA_PERSIST_PATH` | Path to ChromaDB storage | `./chromadb_store` |
| `SECRET_KEY` | Secret key for session management | `changeme` |
| `PORT` | API server port | `8000` |
| `MAX_TOKENS` | Max tokens for LLM response | `2000` |
| `CONFIDENCE_THRESHOLD` | Confidence threshold for escalation | `0.70` |
