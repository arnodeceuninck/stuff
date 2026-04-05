from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend_framework import create_app
from backend_framework.auth import create_auth_proxy_router
from backend_framework.dependencies import init_db

from src.auth_hooks import ensure_local_user_exists
from src.handlers.items import router as items_router
from src.handlers.locations import router as locations_router
from src.handlers.users import router as users_router


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    await init_db()
    yield


app = create_app(title="Stuff API", lifespan_hooks=lifespan)
frontend_origins = [
    origin.strip()
    for origin in os.getenv(
        "FRONTEND_ORIGINS",
        "http://localhost:3000,http://localhost:5173,http://localhost:4173",
    ).split(",")
    if origin.strip()
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=frontend_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(create_auth_proxy_router(on_auth_success=ensure_local_user_exists))
app.include_router(users_router)
app.include_router(locations_router)
app.include_router(items_router)