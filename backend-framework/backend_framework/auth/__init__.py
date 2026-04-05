from backend_framework.auth.dependencies import get_current_user
from backend_framework.auth.jwt import create_access_token, decode_token
from backend_framework.auth.proxy import AuthEvent, AuthSuccessHook, create_auth_proxy_router
from backend_framework.auth.schemas import (
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    TokenPayload,
    TokenResponse,
)

__all__ = [
    "AuthEvent",
    "AuthSuccessHook",
    "LoginRequest",
    "RefreshRequest",
    "RegisterRequest",
    "TokenPayload",
    "TokenResponse",
    "create_access_token",
    "create_auth_proxy_router",
    "decode_token",
    "get_current_user",
]