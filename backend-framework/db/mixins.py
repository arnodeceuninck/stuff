from datetime import datetime
from sqlalchemy import Column, DateTime, String
from sqlalchemy.orm import DeclarativeBase

class AuditMixin:
    modified_date = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    modified_by = Column(String, nullable=True)
    created_date = Column(DateTime, default=datetime.utcnow)

class Base(AuditMixin, DeclarativeBase):
    pass