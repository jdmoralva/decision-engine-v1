import logging
from uuid import uuid4

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from backend.app.application.observability import log_event, now_seconds, reset_request_id, set_request_id
from backend.app.api.schemas.contracts import ContractError, StructuredErrorResponse
from backend.app.api.routes.admin import router as admin_router
from backend.app.api.routes.attachments import router as attachments_router
from backend.app.api.routes.audit import router as audit_router
from backend.app.api.routes.auth import router as auth_router
from backend.app.api.routes.credit_requests import router as credit_requests_router
from backend.app.api.routes.engine_admin import router as engine_admin_router
from backend.app.api.routes.evaluations import router as evaluations_router
from backend.app.api.routes.health import router as health_router
from backend.app.api.routes.loan_consultations import router as loan_consultations_router
from backend.app.config.settings import get_settings
from backend.app.security.exceptions import AuthenticationRequiredError, InvalidTokenError, PermissionDeniedError


settings = get_settings()

logging.basicConfig(level=getattr(logging, settings.log_level, logging.INFO))
http_logger = logging.getLogger("decision_engine.http")

app = FastAPI(title=settings.app_name)


@app.middleware("http")
async def add_request_tracing(request: Request, call_next):
    header_name = settings.request_id_header_name
    request_id = request.headers.get(header_name) or str(uuid4())
    token = set_request_id(request_id)
    request.state.request_id = request_id
    started_at = now_seconds()
    try:
        response = await call_next(request)
    finally:
        reset_request_id(token)

    response.headers[header_name] = request_id
    log_event(
        http_logger,
        logging.INFO,
        "http_request_completed",
        request_id=request_id,
        method=request.method,
        path=request.url.path,
        status_code=response.status_code,
        duration_ms=round((now_seconds() - started_at) * 1000, 2),
    )
    return response


def _structured_error_response(status_code: int, code: str, message: str) -> JSONResponse:
    payload = StructuredErrorResponse(error=ContractError(code=code, message=message))
    return JSONResponse(status_code=status_code, content=payload.model_dump())


@app.exception_handler(AuthenticationRequiredError)
async def handle_authentication_required(_request: Request, exc: AuthenticationRequiredError) -> JSONResponse:
    return _structured_error_response(
        status_code=status.HTTP_401_UNAUTHORIZED,
        code="AUTHENTICATION_REQUIRED",
        message=exc.message,
    )


@app.exception_handler(InvalidTokenError)
async def handle_invalid_token(_request: Request, exc: InvalidTokenError) -> JSONResponse:
    return _structured_error_response(
        status_code=status.HTTP_401_UNAUTHORIZED,
        code="INVALID_TOKEN",
        message=exc.message,
    )


@app.exception_handler(PermissionDeniedError)
async def handle_permission_denied(_request: Request, exc: PermissionDeniedError) -> JSONResponse:
    return _structured_error_response(
        status_code=status.HTTP_403_FORBIDDEN,
        code="FORBIDDEN",
        message=exc.message,
    )


app.include_router(health_router, prefix=settings.api_v1_prefix)
app.include_router(auth_router, prefix=settings.api_v1_prefix)
app.include_router(admin_router, prefix=settings.api_v1_prefix)
app.include_router(audit_router, prefix=settings.api_v1_prefix)
app.include_router(engine_admin_router, prefix=settings.api_v1_prefix)
app.include_router(loan_consultations_router, prefix=settings.api_v1_prefix)
app.include_router(evaluations_router, prefix=settings.api_v1_prefix)
app.include_router(credit_requests_router, prefix=settings.api_v1_prefix)
app.include_router(attachments_router, prefix=settings.api_v1_prefix)
