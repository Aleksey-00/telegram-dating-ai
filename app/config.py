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

    user_name: str = ""
    user_age: int | None = None
    user_city: str = ""

    user_occupation: str = ""
    user_occupation_description: str = ""

    user_interests: str = ""
    user_books: str = ""

    user_travel_countries: str = ""
    user_travel_destination: str = ""
    user_travel_preferences: str = ""
    user_travel_interests: str = ""

    user_lifestyle: str = ""
    user_personality: str = ""

    user_dating_preferences: str = ""
    user_communication_style: str = ""
    user_relationship_goals: str = ""

    user_additional_context: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
