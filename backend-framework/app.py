# framework/app.py
from contextlib import asynccontextmanager
from fastapi import FastAPI

def create_app(lifespan_hooks=None) -> FastAPI:
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        await setup_db()
        await setup_metrics()  # Grafana/Prometheus
        if lifespan_hooks:
            async with lifespan_hooks(app):
                yield
        else:
            yield
        await teardown_db()

    return FastAPI(lifespan=lifespan)