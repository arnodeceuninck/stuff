from functools import lru_cache

from backend_framework.config import FrameworkSettings


class AuthSettings(FrameworkSettings):
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 30


@lru_cache
def get_settings() -> AuthSettings:
    return AuthSettings()
