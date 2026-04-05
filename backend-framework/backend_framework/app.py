from collections.abc import AsyncIterator, Callable
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI

from backend_framework.config import FrameworkSettings
from backend_framework.logging_config import (
    RequestLoggingMiddleware,
    setup_logging,
    unhandled_exception_handler,
)

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
    settings = FrameworkSettings()
    service_name = settings.service_name or title
    setup_logging(
        log_level=settings.log_level,
        log_json=settings.log_json,
        service=service_name,
        environment=settings.environment,
    )

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        if lifespan_hooks is not None:
            async with lifespan_hooks(app):
                yield
            return

        yield

    app = FastAPI(
        title=title,
        docs_url=docs_url,
        redoc_url=redoc_url,
        openapi_url=openapi_url,
        lifespan=lifespan,
        **fastapi_kwargs,
    )
    app.add_middleware(RequestLoggingMiddleware)
    app.add_exception_handler(Exception, unhandled_exception_handler)
    return app