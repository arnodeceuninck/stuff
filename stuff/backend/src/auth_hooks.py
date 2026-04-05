from backend_framework.auth.proxy import AuthEvent
from backend_framework.auth.schemas import TokenPayload
from backend_framework.dependencies import session_scope
from src.handlers.users import ensure_user_exists


async def ensure_local_user_exists(_: AuthEvent, token_payload: TokenPayload) -> None:
    async with session_scope() as db:
        await ensure_user_exists(token_payload, db)
