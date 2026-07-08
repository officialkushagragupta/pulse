"""Service configuration, loaded from this service's own .env (MCP_CLIENT_ prefix)."""
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="MCP_CLIENT_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    ollama_base_url: str
    base_model: str
    port: int = 8200
    log_level: str = "INFO"  # sourced from MCP_CLIENT_LOG_LEVEL in .env


@lru_cache
def get_settings() -> Settings:
    return Settings()
