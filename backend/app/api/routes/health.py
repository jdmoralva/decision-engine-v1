from fastapi import APIRouter

from backend.app.config.settings import get_settings


router = APIRouter(tags=["health"])


@router.get("/health")
def get_health() -> dict[str, str]:
    settings = get_settings()
    return {
        "status": "ok",
        "service": settings.app_name,
        "environment": settings.app_env,
    }
