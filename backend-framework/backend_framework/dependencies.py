from sqlalchemy.ext.asyncio import AsyncSession

from backend_framework.auth.dependencies import get_current_user as get_current_user


async def get_db() -> AsyncSession: ...