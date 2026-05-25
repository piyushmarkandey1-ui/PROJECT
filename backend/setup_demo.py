import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.db import init_db, create_tables
from database.company_store import (
    create_company,
    get_company_by_slug,
    delete_company,
)
from models.schemas import CompanyCreate


def main():
    print("=" * 60)
    print("Setting up Demo Company")
    print("=" * 60)
    print()

    # Initialize database first
    print("Initializing database and creating tables...")
    init_db()
    create_tables()
    print("Database initialized and tables created!")
    print()

    # Delete existing demo company if exists
    demo_slug = "demo-company"
    existing = get_company_by_slug(demo_slug)
    if existing:
        print(f"Deleting existing demo company: {demo_slug}")
        delete_company(demo_slug)
        print()

    # Create new demo company
    demo_company = CompanyCreate(
        name="Demo Corporation",
        slug=demo_slug,
        email="support@demo-corp.com",
        contact_phone="555-123-4567",
        api_key="demo_company_secure_api_key_1234567890abcdef",
    )

    created = create_company(demo_company)
    print(f"Demo company created successfully!")
    print(f"   Name: {created.name}")
    print(f"   Slug: {created.slug}")
    print(f"   Email: {created.email}")
    print()
    print("=" * 60)
    print("Demo company is ready to use!")
    print("=" * 60)


if __name__ == "__main__":
    main()
