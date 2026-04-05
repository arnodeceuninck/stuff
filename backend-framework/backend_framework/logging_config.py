from __future__ import annotations

import json
import logging
import sys
import time
from datetime import UTC, datetime
from typing import Any

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

_CONFIGURED = False


class JsonFormatter(logging.Formatter):
    def __init__(self, *, service: str, environment: str):
        super().__init__()
        self._service = service
        self._environment = environment

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "service": self._service,
            "environment": self._environment,
        }

        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)

        known_fields = {
            "name",
            "msg",
            "args",
            "levelname",
            "levelno",
            "pathname",
            "filename",
            "module",
            "exc_info",
            "exc_text",
            "stack_info",
            "lineno",
            "funcName",
            "created",
            "msecs",
            "relativeCreated",
            "thread",
            "threadName",
            "processName",
            "process",
            "message",
            "asctime",
        }
        for key, value in record.__dict__.items():
            if key not in known_fields and not key.startswith("_"):
                payload[key] = value

        return json.dumps(payload, default=str)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: Any, *, logger_name: str = "backend_framework.request"):
        super().__init__(app)
        self._logger = logging.getLogger(logger_name)

    async def dispatch(self, request: Request, call_next: Any) -> Any:
        start = time.perf_counter()
        response = await call_next(request)
        duration_ms = round((time.perf_counter() - start) * 1000, 2)
        self._logger.info(
            "HTTP request",
            extra={
                "http_method": request.method,
                "http_path": request.url.path,
                "status_code": response.status_code,
                "duration_ms": duration_ms,
                "client_host": request.client.host if request.client else None,
            },
        )
        return response


def setup_logging(*, log_level: str, log_json: bool, service: str, environment: str) -> None:
    global _CONFIGURED
    if _CONFIGURED:
        return

    level = getattr(logging, log_level.upper(), logging.INFO)
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    handler = logging.StreamHandler(sys.stdout)
    if log_json:
        handler.setFormatter(JsonFormatter(service=service, environment=environment))
    else:
        handler.setFormatter(
            logging.Formatter(
                "%(asctime)s %(levelname)s [%(name)s] %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
        )

    root_logger.handlers.clear()
    root_logger.addHandler(handler)

    # Let uvicorn loggers propagate through the same handler to keep one format.
    for logger_name in ("uvicorn", "uvicorn.error", "uvicorn.access"):
        logger = logging.getLogger(logger_name)
        logger.handlers.clear()
        logger.propagate = True

    _CONFIGURED = True


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger = logging.getLogger("backend_framework.error")
    logger.exception(
        "Unhandled exception",
        extra={
            "http_method": request.method,
            "http_path": request.url.path,
            "client_host": request.client.host if request.client else None,
        },
    )
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )
