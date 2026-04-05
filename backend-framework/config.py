from pathlib import Path

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

_SECRETS_DIR = Path("/run/secrets")


class FrameworkSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        secrets_dir=_SECRETS_DIR if _SECRETS_DIR.is_dir() else None,
    )

    database_url: SecretStr
    auth_secret: SecretStr
    grafana_push_url: str | None = None