from fastapi import FastAPI

from backend.app.api.routes.admin import router as admin_router
from backend.app.api.routes.auth import router as auth_router
from backend.app.api.routes.credit_requests import router as credit_requests_router
from backend.app.api.routes.evaluations import router as evaluations_router
from backend.app.api.routes.health import router as health_router
from backend.app.config.settings import get_settings


settings = get_settings()

app = FastAPI(title=settings.app_name)
app.include_router(health_router, prefix=settings.api_v1_prefix)
app.include_router(auth_router, prefix=settings.api_v1_prefix)
app.include_router(admin_router, prefix=settings.api_v1_prefix)
app.include_router(evaluations_router, prefix=settings.api_v1_prefix)
app.include_router(credit_requests_router, prefix=settings.api_v1_prefix)
