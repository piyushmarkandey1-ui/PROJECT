# Architecture Overview

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                              Frontend (React)                            │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐    │
│  │   Chat Widget    │  │  Company Admin   │  │  Escalation UI   │    │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘    │
└─────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         FastAPI Backend (Python)                        │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │  API Layer  │                                                      │  │
│  ├──────────────┴───────────────────────────────────────────────────┤  │
│  │  Authentication (API Keys)  │  Company CRUD  │  Chat Service  │  │
│  ├──────────────────────────────┼─────────────────┼────────────────┤  │
│  │  Guardrails Engine  │  Session Manager  │  Escalation Engine  │  │
│  ├──────────────────────┼───────────────────┼─────────────────────┤  │
│  │                    RAG Service Layer                    │          │  │
│  │  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────┐ │  │
│  │  │  Document Loader │  │   Embedding      │  │   Retriever   │ │  │
│  │  └──────────────────┘  └──────────────────┘  └──────────────┘ │  │
│  └───────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────┘
                                      │
                  ┌───────────────────┴───────────────────┐
                  ▼                                       ▼
┌──────────────────────────────────┐  ┌──────────────────────────────────┐
│      SQL Database (SQLite/       │  │   Vector Database (ChromaDB)    │
│      PostgreSQL)                 │  │   (Company-Specific Collections) │
│  ┌────────────────────────────┐  │  │  ┌────────────────────────────┐  │
│  │    Companies Table         │  │  │  │  kb_acme-corp              │  │
│  │    (Profiles & API Keys)   │  │  │  │  kb_other-company          │  │
│  └────────────────────────────┘  │  │  └────────────────────────────┘  │
└──────────────────────────────────┘  └──────────────────────────────────┘
```

## Key Components

### 1. Frontend (React)
- **Chat Widget**: Customer-facing chat interface
- **Company Admin**: Dashboard for managing company profile and knowledge base
- **Escalation UI**: Notification system for human agent escalations

### 2. Backend (FastAPI)
- **API Layer**: RESTful API endpoints
- **Authentication**: API key-based authentication
- **Chat Service**: Orchestrates the chat flow
- **Guardrails Engine**: Topic filtering and PII sanitization
- **Session Manager**: Conversation history management
- **Escalation Engine**: Automatic escalation logic
- **RAG Service**: Retrieval-Augmented Generation system

### 3. Databases

#### SQL Database (SQLite/PostgreSQL)
- Stores company profiles
- Stores API key hashes
- Manages company metadata

#### Vector Database (ChromaDB)
- Stores vector embeddings of company knowledge bases
- Each company has its own isolated collection
- Supports semantic search

## Data Flow

### Chat Flow
1. Customer sends message to `/api/chat` with `company_slug`
2. System verifies company exists
3. Retrieves relevant documents from company's ChromaDB collection
4. Builds prompt with context, guardrails, and session history
5. Queries Gemini Flash LLM
6. Applies escalation logic if needed
7. Returns response to frontend

### Knowledge Base Upload Flow
1. Company sends CSV with API key in `X-API-Key` header
2. System authenticates and identifies company
3. Parses and processes CSV
4. Generates embeddings
5. Stores in company-specific ChromaDB collection
6. Returns success response
