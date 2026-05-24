# Database Documentation

## Overview

The system uses two databases:
1. **SQL Database** (SQLite/PostgreSQL) - Stores company profiles and metadata
2. **Vector Database** (ChromaDB) - Stores knowledge base embeddings

## Table of Contents

- [Schema](./schema.md)
- [Security](./security.md)
- [Backup & Recovery](./backup.md)

## Database Selection

### Development: SQLite
- File-based, no server required
- Zero configuration
- Perfect for local development

### Production: PostgreSQL
- ACID compliance
- Concurrent connections
- Advanced features
- Better scalability
