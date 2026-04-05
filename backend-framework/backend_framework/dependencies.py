from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from backend_framework.auth.dependencies import get_current_user as get_current_user
from backend_framework.config import FrameworkSettings
from backend_framework.db.mixins import Base

_settings = FrameworkSettings()
_engine = create_async_engine(
    _settings.database_url.get_secret_value(),
    pool_pre_ping=True,
)
_session_factory = async_sessionmaker(_engine, expire_on_commit=False, class_=AsyncSession)


async def get_db() -> AsyncIterator[AsyncSession]:
    async with _session_factory() as session:
        yield session


async def init_db() -> None:
    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)