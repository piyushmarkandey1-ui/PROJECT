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
