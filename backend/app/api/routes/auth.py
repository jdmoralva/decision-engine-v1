from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.api.schemas.auth import LoginRequest, MeResponse, TokenResponse
from backend.app.application.auth import authenticate_user
from backend.app.config.settings import get_settings
from backend.app.infrastructure.db.session import get_db
from backend.app.security.dependencies import get_current_user_context
from backend.app.security.tokens import create_access_token


router = APIRouter(tags=["auth"])


@router.post("/auth/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    authenticated = authenticate_user(db, payload.username, payload.password)
    if authenticated is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    user, _roles = authenticated
    settings = get_settings()
    token = create_access_token(
        subject=user.username,
        secret_key=settings.auth_secret_key,
        expires_in_minutes=settings.access_token_expire_minutes,
    )
    return TokenResponse(access_token=token)


@router.get("/me", response_model=MeResponse)
def me(context: tuple = Depends(get_current_user_context)) -> MeResponse:
    user, roles = context
    return MeResponse(
        id=user.id,
        username=user.username,
        display_name=user.display_name,
        roles=roles,
    )
