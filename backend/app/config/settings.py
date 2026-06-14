import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path


def _parse_bool(raw_value: str, default: bool) -> bool:
    normalized = raw_value.strip().lower()
    if normalized in {"1", "true", "yes", "on"}:
        return True
    if normalized in {"0", "false", "no", "off"}:
        return False
    return default


def _load_env_file() -> None:
    env_file = os.getenv(
        "DECISION_ENGINE_ENV_FILE",
        str(Path(__file__).resolve().parents[3] / ".env"),
    )
    env_path = Path(env_file)
    if not env_path.exists() or not env_path.is_file():
        return

    for line in env_path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue

        key, raw_value = stripped.split("=", 1)
        key = key.strip()
        if not key:
            continue

        value = raw_value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


def _parse_csv(raw_value: str) -> tuple[str, ...]:
    return tuple(item.strip() for item in raw_value.split(",") if item.strip())


@dataclass(frozen=True)
class Settings:
    app_name: str = "decision-engine-api"
    app_env: str = "development"
    api_v1_prefix: str = "/api/v1"
    log_level: str = "INFO"
    request_id_header_name: str = "X-Request-ID"
    database_url: str = "sqlite+pysqlite:///./decision_engine.db"
    auth_secret_key: str = "change-me"
    access_token_expire_minutes: int = 60
    ai_enabled: bool = False
    ai_provider: str = "openai"
    ai_timeout_seconds: float = 20.0
    ai_max_retries: int = 2
    openai_api_key: str | None = None
    openai_model_name: str = "gpt-4.1-mini"
    gemini_api_key: str | None = None
    gemini_model_name: str = "gemini-2.0-flash"
    decision_engine_runtime_builders: tuple[str, ...] = ()
    attachments_storage_dir: str = "./storage/attachments"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    _load_env_file()
    return Settings(
        app_name=os.getenv("APP_NAME", "decision-engine-api"),
        app_env=os.getenv("APP_ENV", "development"),
        api_v1_prefix=os.getenv("API_V1_PREFIX", "/api/v1"),
        log_level=os.getenv("LOG_LEVEL", "INFO").strip().upper(),
        request_id_header_name=os.getenv("REQUEST_ID_HEADER_NAME", "X-Request-ID").strip() or "X-Request-ID",
        database_url=os.getenv("DATABASE_URL", "sqlite+pysqlite:///./decision_engine.db"),
        auth_secret_key=os.getenv("AUTH_SECRET_KEY", "change-me"),
        access_token_expire_minutes=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60")),
        ai_enabled=_parse_bool(os.getenv("AI_ENABLED", "false"), default=False),
        ai_provider=os.getenv("AI_PROVIDER", "openai").strip().lower(),
        ai_timeout_seconds=float(os.getenv("AI_TIMEOUT_SECONDS", "20")),
        ai_max_retries=int(os.getenv("AI_MAX_RETRIES", "2")),
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        openai_model_name=os.getenv("OPENAI_MODEL_NAME", "gpt-4.1-mini"),
        gemini_api_key=os.getenv("GEMINI_API_KEY"),
        gemini_model_name=os.getenv("GEMINI_MODEL_NAME", "gemini-2.0-flash"),
        attachments_storage_dir=os.getenv("ATTACHMENTS_STORAGE_DIR", "./storage/attachments"),
        decision_engine_runtime_builders=_parse_csv(
            os.getenv(
                "DECISION_ENGINE_RUNTIME_BUILDERS",
                "",
            )
        ),
    )


def clear_settings_cache() -> None:
    get_settings.cache_clear()
