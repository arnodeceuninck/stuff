from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, String
from sqlalchemy.orm import DeclarativeBase


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


class AuditMixin:
    modified_date = Column(DateTime(timezone=True), default=_utc_now, onupdate=_utc_now)
    modified_by = Column(String, nullable=True)
    created_date = Column(DateTime(timezone=True), default=_utc_now)


class Base(AuditMixin, DeclarativeBase):
    pass