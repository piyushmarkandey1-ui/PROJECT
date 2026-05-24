# Multi-Tenant AI Customer Care Bot Documentation

Welcome to the complete documentation for the Multi-Tenant AI Customer Care Bot.

## Table of Contents

- [Architecture Overview](./architecture.md)
- [Backend Documentation](./backend/README.md)
  - [Setup Guide](./backend/setup.md)
  - [API Reference](./backend/api.md)
  - [Maintenance Guide](./backend/maintenance.md)
- [Frontend Documentation](./frontend/README.md)
  - [Architecture](./frontend/architecture.md)
  - [Component Specification](./frontend/components.md)
  - [Integration Guide](./frontend/integration.md)
- [Database Documentation](./database/README.md)
  - [Schema](./database/schema.md)
  - [Security](./database/security.md)
  - [Backup & Recovery](./database/backup.md)

## Quick Start

### Backend
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux
pip install -r requirements.txt
cp .env.example .env
# Edit .env and add GEMINI_API_KEY
uvicorn main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

Visit http://localhost:8000/docs for API documentation.
