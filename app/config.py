from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "development"
    app_debug: bool = False

    database_url: str
    redis_url: str

    telegram_api_id: int | None = None
    telegram_api_hash: str | None = None

    llm_api_key: str | None = None
    llm_model: str | None = None
    llm_base_url: str = "http://localhost:11434/v1"
    llm_timeout_seconds: float = 60.0

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
