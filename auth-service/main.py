from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.handlers.auth import router as auth_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # TODO: integrate framework setup_db / setup_metrics when naming conflict
    #       between local app/ package and framework's app.py is resolved
    yield


app = FastAPI(title="Auth Service", lifespan=lifespan)
app.include_router(auth_router)
