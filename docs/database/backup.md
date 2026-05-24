# Backup & Recovery

## Backup Strategy

### Recommended Backup Schedule

| Type | Frequency | Retention |
|------|-----------|-----------|
| Full Backup | Daily | 30 days |
| Incremental | Hourly | 7 days |
| Transaction Log | Continuous | 24 hours |

## SQLite Backup & Recovery

### Backup
```bash
#!/bin/bash
# backup_sqlite.sh

BACKUP_DIR="/path/to/backups"
DATE=$(date +%Y%m%d_%H%M%S)
DB_FILE="customer_care_bot.db"

mkdir -p $BACKUP_DIR
cp $DB_FILE $BACKUP_DIR/customer_care_bot_$DATE.db

# Keep last 30 backups
find $BACKUP_DIR -name "customer_care_bot_*.db" -mtime +30 -delete
```

### Schedule with cron
```bash
# Edit crontab
crontab -e

# Add daily backup at 2 AM
0 2 * * * /path/to/backup_sqlite.sh
```

### Recovery
```bash
# Stop application first
systemctl stop customer-care-bot

# Restore from backup
cp /path/to/backups/customer_care_bot_20240101_020000.db customer_care_bot.db

# Start application
systemctl start customer-care-bot
```

## PostgreSQL Backup & Recovery

### Full Backup (pg_dump)
```bash
#!/bin/bash
# backup_postgres.sh

BACKUP_DIR="/path/to/backups"
DATE=$(date +%Y%m%d_%H%M%S)
DB_NAME="customer_care_bot"
DB_USER="cc_bot_user"

mkdir -p $BACKUP_DIR
pg_dump -U $DB_USER $DB_NAME | gzip > $BACKUP_DIR/${DB_NAME}_$DATE.sql.gz

# Keep last 30 backups
find $BACKUP_DIR -name "${DB_NAME}_*.sql.gz" -mtime +30 -delete
```

### Continuous Archiving (WAL)
```sql
-- postgresql.conf
wal_level = replica
archive_mode = on
archive_command = 'cp %p /path/to/wal_archive/%f'
```

### Recovery
```bash
# Stop PostgreSQL
systemctl stop postgresql

# Restore base backup
gunzip -c /path/to/backups/customer_care_bot_20240101_020000.sql.gz | psql -U cc_bot_user customer_care_bot

# Start PostgreSQL
systemctl start postgresql
```

## ChromaDB Backup & Recovery

### Backup
```bash
#!/bin/bash
# backup_chroma.sh

BACKUP_DIR="/path/to/backups"
DATE=$(date +%Y%m%d_%H%M%S)
CHROMA_DIR="./chromadb_store"

mkdir -p $BACKUP_DIR
tar -czf $BACKUP_DIR/chromadb_$DATE.tar.gz $CHROMA_DIR

# Keep last 30 backups
find $BACKUP_DIR -name "chromadb_*.tar.gz" -mtime +30 -delete
```

### Recovery
```bash
# Stop application first
systemctl stop customer-care-bot

# Remove existing chromadb store
rm -rf ./chromadb_store

# Restore from backup
tar -xzf /path/to/backups/chromadb_20240101_020000.tar.gz

# Start application
systemctl start customer-care-bot
```

## Combined Backup Script

```bash
#!/bin/bash
# full_backup.sh

BACKUP_DIR="/path/to/backups"
DATE=$(date +%Y%m%d_%H%M%S)
LOG_FILE="$BACKUP_DIR/backup_$DATE.log"

exec > >(tee -a $LOG_FILE)
exec 2>&1

echo "Starting backup at $(date)"

# Backup SQLite/PostgreSQL
echo "Backing up SQL database..."
/path/to/backup_sqlite.sh

# Backup ChromaDB
echo "Backing up ChromaDB..."
/path/to/backup_chroma.sh

echo "Backup completed at $(date)"
```

## Cloud Backup

### AWS S3
```bash
# Install AWS CLI
pip install awscli

# Configure
aws configure

# Upload backup
aws s3 cp /path/to/backups/customer_care_bot_20240101_020000.db s3://your-bucket/backups/
```

### Google Cloud Storage
```bash
# Install gcloud CLI
# https://cloud.google.com/sdk/docs/install

# Authenticate
gcloud auth login

# Upload backup
gsutil cp /path/to/backups/customer_care_bot_20240101_020000.db gs://your-bucket/backups/
```

## Disaster Recovery

### RTO & RPO Targets
- **Recovery Time Objective (RTO):** 1 hour
- **Recovery Point Objective (RPO):** 1 hour

### Recovery Steps

1. **Assess Damage**
   - Identify what data is lost
   - Determine cause of failure

2. **Restore Infrastructure**
   - Provision new servers if needed
   - Install dependencies
   - Configure environment

3. **Restore Databases**
   - Restore SQL database from latest backup
   - Restore ChromaDB from latest backup
   - Verify data integrity

4. **Test Application**
   - Start application
   - Run smoke tests
   - Verify functionality

5. **Switch Over**
   - Update DNS/load balancer
   - Monitor application
   - Verify user access

## Backup Verification

### Regular Verification
```bash
#!/bin/bash
# verify_backup.sh

BACKUP_FILE="/path/to/backups/customer_care_bot_latest.db"
TEST_DIR="/tmp/backup_test"

mkdir -p $TEST_DIR
cp $BACKUP_FILE $TEST_DIR/test.db

# Test SQLite
sqlite3 $TEST_DIR/test.db "SELECT COUNT(*) FROM companies;"

# Cleanup
rm -rf $TEST_DIR

echo "Backup verification complete"
```

### Automated Verification
Add to cron:
```bash
0 4 * * * /path/to/verify_backup.sh
```

## Backup Encryption

### Encrypt Backup
```bash
# Encrypt with GPG
gpg --encrypt --recipient your-email@example.com customer_care_bot.db

# Encrypt with OpenSSL
openssl enc -aes-256-cbc -salt -in customer_care_bot.db -out customer_care_bot.db.enc
```

### Decrypt Backup
```bash
# Decrypt with GPG
gpg --decrypt customer_care_bot.db.gpg > customer_care_bot.db

# Decrypt with OpenSSL
openssl enc -d -aes-256-cbc -in customer_care_bot.db.enc -out customer_care_bot.db
```
