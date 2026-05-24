# Backend Maintenance Guide

## Monitoring

### Health Check
Regularly check the health endpoint:
```bash
curl http://localhost:8000/api/health
```

### Logs
Logs are output to stdout. In production, use logging aggregation tools like:
- ELK Stack (Elasticsearch, Logstash, Kibana)
- Datadog
- CloudWatch (AWS)

## Backups

### Database Backup

#### SQLite
```bash
# Create backup
cp customer_care_bot.db customer_care_bot.backup.db

# Restore from backup
cp customer_care_bot.backup.db customer_care_bot.db
```

#### PostgreSQL
```bash
# Create backup
pg_dump -U username -h hostname database_name > backup.sql

# Restore from backup
psql -U username -h hostname database_name < backup.sql
```

### ChromaDB Backup
```bash
# Create backup
tar -czf chromadb_backup.tar.gz ./chromadb_store

# Restore from backup
tar -xzf chromadb_backup.tar.gz
```

## Scaling

### Horizontal Scaling
- Use a process manager like Gunicorn with multiple workers
- Deploy behind a load balancer
- Use PostgreSQL instead of SQLite for multi-process access

### Vertical Scaling
- Increase server resources (CPU, memory)
- Optimize LLM response caching
- Use faster embedding models

## Updating

### Deploying Updates
```bash
cd backend
git pull origin main
pip install -r requirements.txt
# Restart the service
```

### Database Migrations
For production, use Alembic for schema migrations:
```bash
# Initialize Alembic (first time)
alembic init alembic

# Create migration
alembic revision --autogenerate -m "description"

# Apply migration
alembic upgrade head
```

## Troubleshooting

### Common Issues

1. **GEMINI_API_KEY not set**
   - Check .env file or environment variables
   - Verify API key is valid and not expired

2. **Database connection errors**
   - Verify DATABASE_URL is correct
   - Check database permissions
   - Ensure database server is running

3. **ChromaDB initialization failed**
   - Check CHROMA_PERSIST_PATH permissions
   - Verify disk space is available
   - Delete corrupted chromadb_store directory and restart

4. **Memory issues**
   - Reduce MAX_TOKENS in config
   - Use smaller embedding models
   - Implement request throttling

## Performance Optimization

### Caching
- Cache frequent LLM responses
- Implement session-based caching
- Use Redis for distributed caching

### Embedding Optimization
- Pre-compute embeddings during off-peak hours
- Use batch processing for knowledge base updates
- Cache embeddings in Redis

### Database Optimization
- Index frequently queried columns
- Use connection pooling
- Regularly vacuum/analyze database
