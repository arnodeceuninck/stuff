from functools import lru_cache

from config import FrameworkSettings


class AuthSettings(FrameworkSettings):
    access_token_expire_minutes: int = 60


@lru_cache
def get_settings() -> AuthSettings:
    return AuthSettings()
