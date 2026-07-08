"""Service configuration, from this service's own .env (KNOWLEDGE_BASE_MCP_SERVER_ prefix)."""
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="KNOWLEDGE_BASE_MCP_SERVER_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    ollama_base_url: str
    embedding_model: str
    port: int = 8100
    log_level: str = "INFO"  # sourced from KNOWLEDGE_BASE_MCP_SERVER_LOG_LEVEL in .env


@lru_cache
def get_settings() -> Settings:
    return Settings()
