# 🤖 AI Customer Care Bot

![Python](https://img.shields.io/badge/Python-3.11-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green)
![React](https://img.shields.io/badge/React-18-61DAFB)
![ChromaDB](https://img.shields.io/badge/ChromaDB-0.5-orange)
![Gemini](https://img.shields.io/badge/Gemini-Flash-purple)

A production-grade AI-powered customer care chatbot built with a **Retrieval-Augmented Generation (RAG)** architecture. The system uses **Gemini Flash** as the LLM, **ChromaDB** as the vector database for semantic search over your company's knowledge base, and a modular 9-layer service design that handles conversation memory, automatic escalation to human agents, PII guardrails, and on-device session management — all deployable in under 6 hours.

---

## Architecture

```
User (React Frontend)
        │
        ▼
FastAPI Backend
  ├── GuardrailsEngine   — topic filter + PII sanitization
  ├── SessionManager     — in-memory conversation history
  ├── Retriever          — ChromaDB semantic search (RAG)
  ├── ChatHandler        — Gemini Flash LLM orchestration
  └── EscalationEngine   — auto-escalate on low confidence / negative sentiment
        │
        ▼
ChromaDB (Vector Store)  ←  KnowledgeBaseBuilder (CSV / PDF / dict)
```

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| LLM | Google Gemini Flash (`gemini-2.0-flash`) |
| Embeddings | Google `text-embedding-004` |
| Vector DB | ChromaDB (persistent) |
| Backend | FastAPI + Uvicorn |
| Frontend | React 18 + Vite + Tailwind CSS |
| Deploy (BE) | Railway |
| Deploy (FE) | Vercel |

---

## Setup

### 1. Clone & configure

```bash
git clone <your-repo-url>
cd customer-care-bot
```

### 2. Backend

```bash
cd backend
python -m venv venv
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

pip install -r requirements.txt
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY
```

### 3. Run backend

```bash
uvicorn main:app --reload --port 8000
```

### 4. Frontend

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/chat` | Send a message, get a response |
| `POST` | `/api/session/new` | Create a new session |
| `GET` | `/api/session/{id}/history` | Get conversation history |
| `DELETE` | `/api/session/{id}` | Clear a session |
| `POST` | `/api/knowledge/upload-csv` | Upload a FAQ CSV |
| `GET` | `/api/knowledge/stats` | Knowledge base stats |
| `GET` | `/api/health` | Health check |

---

## Running Tests

```bash
cd backend
python test_bot.py
```

---

## Deploy

### Backend → Railway

```bash
cd backend
railway login
railway init
railway up
```

### Frontend → Vercel

```bash
cd frontend
npm run build
vercel --prod
```

Set `VITE_API_URL` in Vercel environment variables to your Railway backend URL.

---

## FlowZint Hackathon Submission

Built for the FlowZint Hackathon. This project demonstrates a complete, production-ready AI customer care solution with RAG, LLM orchestration, escalation logic, and a polished React UI — all implemented in a single hackathon session.

---

## Demo

> 📹 Demo video: _[Add your YouTube/Drive link here]_  
> 🌐 Live URL: _[Add your Vercel URL here]_
