"""
Migration script to add password_hash column to companies table.
Run this script to update existing databases.
"""
import sqlite3
import sys
from pathlib import Path

# Add parent directory to path to import from database
sys.path.insert(0, str(Path(__file__).parent.parent))

from database.company_db import get_db_session
from database.models import Base
from sqlalchemy import text


def migrate_add_password_hash():
    """Add password_hash column to companies table."""
    with get_db_session() as session:
        try:
            # Check if column already exists
            result = session.execute(text("PRAGMA table_info(companies)"))
            columns = [row[1] for row in result.fetchall()]
            
            if 'password_hash' in columns:
                print("password_hash column already exists. Skipping migration.")
                return
            
            # Add the column
            session.execute(text("ALTER TABLE companies ADD COLUMN password_hash TEXT"))
            session.commit()
            print("Successfully added password_hash column to companies table.")
            
        except Exception as e:
            session.rollback()
            print(f"Migration failed: {e}")
            raise


if __name__ == "__main__":
    migrate_add_password_hash()
