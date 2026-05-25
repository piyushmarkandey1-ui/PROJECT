# Database Schema

## SQL Database

### Companies Table

**Table name:** `companies`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | VARCHAR(36) | PRIMARY KEY | UUID v4 |
| `name` | VARCHAR(100) | NOT NULL, INDEXED | Display name |
| `slug` | VARCHAR(50) | UNIQUE, NOT NULL, INDEXED | URL-safe identifier (auto-generated) |
| `email` | VARCHAR(255) | NOT NULL | Contact email |
| `contact_phone` | VARCHAR(50) | NULLABLE | Contact phone |
| `api_key_hash` | TEXT | NOT NULL, INDEXED | SHA-256 hash of API key |
| `created_at` | DATETIME | NOT NULL | UTC creation timestamp |
| `updated_at` | DATETIME | NOT NULL | UTC last-update timestamp |

**Indexes:**
- PRIMARY KEY on `id`
- UNIQUE INDEX on `slug`
- INDEX on `name`
- INDEX on `api_key_hash` (for fast API key lookups)

**SQLAlchemy model:**
```python
class Company(Base):
    __tablename__ = "companies"

    id           = Column(String(36), primary_key=True, index=True)
    name         = Column(String(100), nullable=False, index=True)
    slug         = Column(String(50), unique=True, nullable=False, index=True)
    email        = Column(String(255), nullable=False)
    contact_phone= Column(String(50), nullable=True)
    api_key_hash = Column(Text, nullable=False, index=True)
    created_at   = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at   = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
```

---

## API Key Generation & Storage

```python
import secrets, string, hashlib

def _generate_api_key(length: int = 32) -> str:
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def _hash_api_key(api_key: str) -> str:
    return hashlib.sha256(api_key.encode("utf-8")).hexdigest()
```

- Plaintext key returned **once** at creation — never stored
- All subsequent lookups compare SHA-256 hashes

---

## Slug Generation

```python
def _generate_slug(name: str) -> str:
    slug = name.lower().strip()
    slug = ''.join(c if c.isalnum() or c == ' ' else '-' for c in slug)
    slug = slug.replace(' ', '-').replace('--', '-').rstrip('-')
    if len(slug) < 3:
        slug = slug + str(uuid.uuid4())[:3]
    return slug[:50]
```

On collision, a Unix timestamp suffix is appended: `acme-corp-1748123456`.

---

## Vector Database (ChromaDB)

### Collection Naming
```
kb_{company_slug}
```

Examples:
- `acme-corp` → `kb_acme-corp`
- `tech solutions` → `kb_tech-solutions`

### Collection Metadata
```json
{
  "hnsw:space": "cosine",
  "company_slug": "acme-corp"
}
```

### Document Structure
```python
{
  "id": "uuid4-string",
  "document": "Q: How do I track my order?\nA: Once your order ships...",
  "metadata": {
    "source": "/tmp/tmpXXXXXX.csv",
    "category": "faq",
    "timestamp": "2026-05-25T10:00:00.000000"
  },
  "embedding": [...]   # 384-dimensional float vector (all-MiniLM-L6-v2)
}
```

### Retrieval Parameters
- `n_results`: 3 (top-3 most similar documents)
- `MIN_SCORE`: 0.30 (minimum cosine similarity to include)
- `RELEVANCE_THRESHOLD`: 0.25 (threshold for `is_relevant()` check)
- Distance → score conversion: `score = 1 - (distance / 2)`

---

## Data Relationships

```
companies (SQL)          ChromaDB
─────────────────        ──────────────────────────
id (UUID)                kb_{slug} collection
name                       └── documents[]
slug ──────────────────────────> metadata.company_slug
email
api_key_hash
```

- No foreign keys between SQL and ChromaDB — linked by `company_slug` string
- Deleting a company also deletes its ChromaDB collection (`reset_collection()`)

---

## Migration: SQLite → PostgreSQL

1. Set `DATABASE_URL` to PostgreSQL connection string in `.env`
2. Restart — SQLAlchemy auto-creates tables
3. Migrate existing data:

```bash
pip install pgloader
pgloader sqlite:///customer_care_bot.db postgresql://user:pass@host/db
```
