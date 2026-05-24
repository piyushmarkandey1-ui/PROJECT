# Database Security

## Authentication & Authorization

### API Key Authentication
- API keys are never stored in plain text
- SHA-256 hashing used for API key storage
- Hash comparison uses constant-time comparison to prevent timing attacks

**Hashing Implementation:**
```python
import hashlib

def _hash_api_key(api_key: str) -> str:
    return hashlib.sha256(api_key.encode("utf-8")).hexdigest()
```

### Company Isolation
- Each company has its own ChromaDB collection
- SQL queries are parameterized to prevent SQL injection
- API endpoints validate company ownership before modifications

## Data Encryption

### At Rest
- SQLite: File system permissions (chmod 600)
- PostgreSQL: Transparent Data Encryption (TDE)
- ChromaDB: File system permissions

### In Transit
- TLS/SSL for all API communications
- HTTPS required in production
- HSTS headers for production deployments

## Access Controls

### Database User Permissions (PostgreSQL)
```sql
-- Create restricted user
CREATE USER cc_bot_user WITH PASSWORD 'strong-password';

-- Grant minimal permissions
GRANT CONNECT ON DATABASE customer_care_bot TO cc_bot_user;
GRANT USAGE ON SCHEMA public TO cc_bot_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON companies TO cc_bot_user;
```

### File System Permissions
```bash
# SQLite database
chmod 600 customer_care_bot.db

# ChromaDB storage
chmod 700 chromadb_store
chmod 600 chromadb_store/*
```

## Secrets Management

### Environment Variables
Never commit secrets to version control:
```env
# .env (never committed)
GEMINI_API_KEY=your-key
DATABASE_URL=postgresql://user:pass@host/db
SECRET_KEY=your-secret
```

### Production Secrets Management
- Use Railway Variables (Railway)
- Use Vercel Environment Variables (Vercel)
- Use AWS Secrets Manager / HashiCorp Vault for enterprise

## SQL Injection Prevention

### Parameterized Queries
Always use SQLAlchemy's parameterized queries:
```python
# Good
company = session.query(Company).filter(Company.slug == slug).first()

# Bad (never do this)
company = session.execute(f"SELECT * FROM companies WHERE slug = '{slug}'")
```

## Input Validation

### Company Slug Validation
- Regex: `^[a-z0-9-]+$`
- Length: 2-50 characters
- No spaces or special characters

### API Key Validation
- Minimum 32 characters
- Secure random generation
- No predictable patterns

## Audit Logging

### Logged Events
- Company creation
- Company updates
- Company deletion
- Knowledge base uploads
- API authentication attempts

### Log Format
```json
{
  "timestamp": "2024-01-01T00:00:00Z",
  "event": "company_created",
  "company_slug": "acme-corp",
  "ip_address": "192.168.1.1",
  "user_agent": "Mozilla/5.0..."
}
```

## Security Best Practices

1. **Rotate API Keys** - Regularly rotate company API keys
2. **Monitor Access** - Log and monitor all API access
3. **Rate Limiting** - Implement rate limiting to prevent abuse
4. **Regular Audits** - Perform security audits quarterly
5. **Backup Encryption** - Encrypt all backups
6. **Least Privilege** - Apply principle of least privilege
7. **Keep Dependencies Updated** - Regularly update dependencies for security patches
