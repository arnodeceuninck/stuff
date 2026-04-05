from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from backend_framework import create_app
from backend_framework.auth import create_auth_proxy_router
from backend_framework.dependencies import init_db

from src.auth_hooks import ensure_local_user_exists
from src.handlers.users import router as users_router


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    await init_db()
    yield


app = create_app(title="Stuff API", lifespan_hooks=lifespan)
app.include_router(create_auth_proxy_router(on_auth_success=ensure_local_user_exists))
app.include_router(users_router)