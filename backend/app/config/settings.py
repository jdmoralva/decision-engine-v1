from dataclasses import dataclass
from functools import lru_cache
import os


@dataclass(frozen=True)
class Settings:
    app_name: str = "decision-engine-api"
    app_env: str = "development"
    api_v1_prefix: str = "/api/v1"
    database_url: str = "sqlite+pysqlite:///./decision_engine.db"
    auth_secret_key: str = "change-me"
    access_token_expire_minutes: int = 60


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings(
        app_name=os.getenv("APP_NAME", "decision-engine-api"),
        app_env=os.getenv("APP_ENV", "development"),
        api_v1_prefix=os.getenv("API_V1_PREFIX", "/api/v1"),
        database_url=os.getenv("DATABASE_URL", "sqlite+pysqlite:///./decision_engine.db"),
        auth_secret_key=os.getenv("AUTH_SECRET_KEY", "change-me"),
        access_token_expire_minutes=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60")),
    )


def clear_settings_cache() -> None:
    get_settings.cache_clear()
