from collections.abc import AsyncIterator, Callable
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI

AppLifespanHook = Callable[[FastAPI], AsyncIterator[None]]


def create_app(
    *,
    title: str = "API",
    lifespan_hooks: AppLifespanHook | None = None,
    docs_url: str | None = "/docs",
    redoc_url: str | None = "/redoc",
    openapi_url: str | None = "/openapi.json",
    **fastapi_kwargs: Any,
) -> FastAPI:
    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        if lifespan_hooks is not None:
            async with lifespan_hooks(app):
                yield
            return

        yield

    return FastAPI(
        title=title,
        docs_url=docs_url,
        redoc_url=redoc_url,
        openapi_url=openapi_url,
        lifespan=lifespan,
        **fastapi_kwargs,
    )