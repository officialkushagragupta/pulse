"""Service configuration, loaded from this service's own .env (TOOLS_SERVICE_ prefix)."""
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="TOOLS_SERVICE_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    postgres_dsn: str
    port: int = 8000
    log_level: str = "INFO"  # sourced from TOOLS_SERVICE_LOG_LEVEL in .env


@lru_cache
def get_settings() -> Settings:
    return Settings()
