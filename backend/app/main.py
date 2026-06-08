from fastapi import FastAPI

from backend.app.api.routes.health import router as health_router
from backend.app.config.settings import get_settings


settings = get_settings()

app = FastAPI(title=settings.app_name)
app.include_router(health_router, prefix=settings.api_v1_prefix)
