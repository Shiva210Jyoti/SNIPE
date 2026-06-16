from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Central configuration loaded from environment variables.

    Interview angle: never hardcode secrets or URLs in code.
    In production, these come from env vars, Kubernetes secrets, or AWS Parameter Store.
    """

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    app_name: str = "SnipURL"
    debug: bool = False
    database_url: str = "postgresql://snipurl:snipurl@localhost:5432/snipurl"
    base_url: str = "http://localhost:8000"
    short_code_length: int = 7
    redis_url: str = "redis://localhost:6379/0"
    redis_enabled: bool = True
    cache_ttl_seconds: int = 3600
    kafka_bootstrap_servers: str = "localhost:9092"
    kafka_click_topic: str = "url-clicks"
    kafka_consumer_group: str = "snipurl-click-consumers"
    kafka_enabled: bool = True


@lru_cache
def get_settings() -> Settings:
    """Cached settings instance — parsed once per process."""
    return Settings()
