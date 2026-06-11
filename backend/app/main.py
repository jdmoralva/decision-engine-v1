from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from backend.app.api.schemas.contracts import ContractError, StructuredErrorResponse
from backend.app.api.routes.admin import router as admin_router
from backend.app.api.routes.auth import router as auth_router
from backend.app.api.routes.credit_requests import router as credit_requests_router
from backend.app.api.routes.evaluations import router as evaluations_router
from backend.app.api.routes.health import router as health_router
from backend.app.api.routes.loan_consultations import router as loan_consultations_router
from backend.app.config.settings import get_settings
from backend.app.security.exceptions import AuthenticationRequiredError, InvalidTokenError, PermissionDeniedError


settings = get_settings()

app = FastAPI(title=settings.app_name)


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
app.include_router(loan_consultations_router, prefix=settings.api_v1_prefix)
app.include_router(evaluations_router, prefix=settings.api_v1_prefix)
app.include_router(credit_requests_router, prefix=settings.api_v1_prefix)
