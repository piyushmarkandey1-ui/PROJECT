# Database Schema

## SQL Database Schema

### Companies Table

**Table Name:** `companies`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | VARCHAR(36) | PRIMARY KEY | UUID identifier |
| `name` | VARCHAR(100) | NOT NULL, INDEXED | Company display name |
| `slug` | VARCHAR(50) | UNIQUE, NOT NULL, INDEXED | URL-safe company identifier |
| `email` | VARCHAR(255) | NOT NULL | Company contact email |
| `contact_phone` | VARCHAR(50) | NULLABLE | Company phone number |
| `api_key_hash` | TEXT | NOT NULL, INDEXED | SHA-256 hash of API key |
| `created_at` | DATETIME | NOT NULL | Creation timestamp |
| `updated_at` | DATETIME | NOT NULL | Last update timestamp |

### Indexes
- PRIMARY KEY on `id`
- UNIQUE INDEX on `slug`
- INDEX on `name`
- INDEX on `api_key_hash`

## SQLAlchemy Model

```python
from datetime import datetime
from sqlalchemy import Column, DateTime, String, Text
from database.db import Base

class Company(Base):
    __tablename__ = "companies"

    id = Column(String(36), primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    slug = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(255), nullable=False)
    contact_phone = Column(String(50), nullable=True)
    api_key_hash = Column(Text, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
```

## Vector Database (ChromaDB)

### Collection Naming
Each company has its own ChromaDB collection with the format:
```
kb_{company_slug}
```

Example:
- Company: `acme-corp` → Collection: `kb_acme-corp`
- Company: `tech-company` → Collection: `kb_tech-company`

### Collection Structure

**Metadata:**
```json
{
  "hnsw:space": "cosine",
  "company_slug": "acme-corp"
}
```

**Document Structure:**
```python
{
  "id": "uuid",
  "document": "Q: How do I track my order?\nA: Visit Orders > Track Order",
  "metadata": {
    "source": "faqs.csv",
    "category": "shipping",
    "timestamp": "2024-01-01T00:00:00Z"
  },
  "embedding": [0.1, 0.2, 0.3, ...]  # 384-dimensional vector
}
```

## Data Relationships

### Company ↔ Knowledge Base
- One company has one ChromaDB collection
- Collection name is derived from company slug
- No foreign keys (separate databases)

## Migration Guide

### SQLite → PostgreSQL
1. Set `DATABASE_URL` to PostgreSQL connection string
2. Restart application (tables auto-created)
3. Migrate existing data using tools like `pgloader`

### Example Migration with pgloader
```bash
pgloader sqlite:///customer_care_bot.db postgresql://user:pass@host/db
```
