import os

from pydantic import BaseModel


def _as_bool(value: str | None, default: bool) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


class Settings(BaseModel):
    app_name: str = "Grand Summoners Companion API"
    app_version: str = "0.1.0"
    api_prefix: str = "/api/v1"
    database_url: str | None = None
    persistence_enabled: bool = False


settings = Settings(
    database_url=os.getenv("DATABASE_URL"),
    persistence_enabled=_as_bool(os.getenv("PERSISTENCE_ENABLED"), False),
)
