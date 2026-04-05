from backend_framework import create_app

from src.handlers.users import router as users_router


app = create_app(title="Stuff API")
app.include_router(users_router)