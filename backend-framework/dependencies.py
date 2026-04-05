# framework/dependencies.py — inject framework services as FastAPI deps
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from auth.dependencies import get_current_user as get_current_user  # noqa: F401 — re-export


async def get_db() -> AsyncSession: ...