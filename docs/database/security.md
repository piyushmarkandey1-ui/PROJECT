# Database Security

## API Key Security

### Generation
API keys are generated using Python's `secrets` module — cryptographically secure random:
```python
import secrets, string

def _generate_api_key(length: int = 32) -> str:
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))
```

### Storage
Only the SHA-256 hash is stored — the plaintext key is **never persisted**:
```python
import hashlib

def _hash_api_key(api_key: str) -> str:
    return hashlib.sha256(api_key.encode("utf-8")).hexdigest()
```

### Lookup
```python
def get_company_by_api_key(api_key: str) -> Optional[CompanySchema]:
    api_key_hash = _hash_api_key(api_key)
    # Query by hash — constant-time comparison via DB index
    company = session.query(Company).filter(Company.api_key_hash == api_key_hash).first()
```

---

## Company Isolation

- Each company's ChromaDB collection is named `kb_{slug}` — no cross-company access
- Sessions are keyed by `(company_slug, session_id)` — company A cannot read company B's sessions
- API key authentication enforces company ownership on all write operations:
  - `PUT /api/companies/{slug}` — only the company's own key can update
  - `DELETE /api/companies/{slug}` — only the company's own key can delete
  - `POST /api/knowledge/upload-csv` — only the company's own key can upload

---

## SQL Injection Prevention

All queries use SQLAlchemy ORM with parameterized statements:
```python
# Safe — parameterized
company = session.query(Company).filter(Company.slug == slug).first()

# Never do this
session.execute(f"SELECT * FROM companies WHERE slug = '{slug}'")
```

---

## PII Sanitization

The `GuardrailsEngine` automatically redacts PII from LLM responses:

| Pattern | Replacement |
|---------|-------------|
| Credit card numbers (13-16 digits) | `[REDACTED-CC]` |
| SSNs (`XXX-XX-XXXX`) | `[REDACTED-SSN]` |
| Passwords (`password: value`) | `password: [REDACTED]` |

```python
_CC_PATTERN       = re.compile(r"\b(?:\d[ -]?){13,16}\b")
_SSN_PATTERN      = re.compile(r"\b\d{3}[-\s]?\d{2}[-\s]?\d{4}\b")
_PASSWORD_PATTERN = re.compile(r"(?i)(password\s*[:=]\s*\S+)")
```

---

## Secrets Management

### Development
```env
# .env — never commit to git
GEMINI_API_KEY=your-key
GOOGLE_API_KEY=your-key
DATABASE_URL=sqlite:///./customer_care_bot.db
SECRET_KEY=your-secret
```

The `.gitignore` excludes `.env` by default.

### Production (Railway)
```bash
railway variables set GEMINI_API_KEY=your-key
railway variables set GOOGLE_API_KEY=your-key
railway variables set DATABASE_URL=postgresql://...
railway variables set SECRET_KEY=your-production-secret
```

---

## File System Permissions

```bash
# SQLite database — owner read/write only
chmod 600 customer_care_bot.db

# ChromaDB store — owner read/write/execute
chmod 700 chromadb_store
```

---

## Production Checklist

- [ ] `SECRET_KEY` is a long random string (not `changeme`)
- [ ] `DATABASE_URL` points to PostgreSQL (not SQLite)
- [ ] `.env` is in `.gitignore` and not committed
- [ ] CORS `allow_origins` restricted to your frontend domain
- [ ] HTTPS enforced (Railway and Vercel do this automatically)
- [ ] API keys rotated if compromised (delete company, recreate)
