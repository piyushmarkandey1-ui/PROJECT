# Backup & Recovery

## What to Back Up

| Data | Location | Criticality |
|------|----------|-------------|
| Company profiles + API key hashes | `companies.db` | **Critical** |
| Knowledge base embeddings | `chromadb_store/` | High (re-uploadable from CSVs) |
| FAQ CSV source files | `backend/data/*.csv` | Medium (source of truth for KB) |

---

## SQLite Backup

### Manual
```bash
cp companies.db companies.backup.$(date +%Y%m%d).db
```

### Automated (cron)
```bash
# backup_sqlite.sh
BACKUP_DIR="./backups"
mkdir -p $BACKUP_DIR
cp companies.db $BACKUP_DIR/companies_$(date +%Y%m%d_%H%M%S).db
# Keep last 30 days
find $BACKUP_DIR -name "customer_care_bot_*.db" -mtime +30 -delete
```

```bash
# Add to crontab — daily at 2 AM
0 2 * * * /path/to/backup_sqlite.sh
```

### Restore
```bash
# Stop server first
cp backups/companies_20260525_020000.db companies.db
# Restart server
```

---

## PostgreSQL Backup

### Backup
```bash
pg_dump -U username -h hostname database_name | gzip > backup_$(date +%Y%m%d).sql.gz
```

### Restore
```bash
gunzip -c backup_20260525.sql.gz | psql -U username -h hostname database_name
```

---

## ChromaDB Backup

ChromaDB stores data as binary files in `chromadb_store/`. Back up the entire directory.

### Backup
```bash
tar -czf chromadb_backup_$(date +%Y%m%d).tar.gz ./chromadb_store
```

### Restore
```bash
rm -rf ./chromadb_store
tar -xzf chromadb_backup_20260525.tar.gz
# Restart server
```

### Alternative: Re-upload from CSVs
If you have the original CSV files, you can rebuild the knowledge base:
```bash
# For each company
curl -X POST http://localhost:8000/api/knowledge/upload-csv \
  -H "X-API-Key: <company-api-key>" \
  -F "file=@backend/data/sample_faqs.csv"
```

---

## Recovery Procedure

1. **Stop the server**
2. **Restore SQL database** (company profiles + API keys)
3. **Restore ChromaDB** (or re-upload CSVs)
4. **Start the server**
5. **Verify** with health check: `curl http://localhost:8000/api/health`

---

## Railway Production Backup

Railway provides automatic PostgreSQL backups on paid plans. For manual backup:
```bash
railway run pg_dump $COMPANY_DATABASE_URL > backup_$(date +%Y%m%d).sql
```

For ChromaDB on Railway, use a persistent volume and back it up via the Railway dashboard or CLI.
