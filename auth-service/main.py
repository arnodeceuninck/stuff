from backend_framework import create_app

from app.handlers.auth import router as auth_router


app = create_app(title="Auth Service")
app.include_router(auth_router)
