from collections.abc import Callable

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from backend.app.application.auth import get_user_by_username, get_user_roles, user_has_any_role
from backend.app.config.settings import get_settings
from backend.app.infrastructure.db.models import User
from backend.app.infrastructure.db.session import get_db
from backend.app.security.tokens import decode_access_token


http_bearer = HTTPBearer(auto_error=False)


def get_current_user_context(
    credentials: HTTPAuthorizationCredentials | None = Depends(http_bearer),
    db: Session = Depends(get_db),
) -> tuple[User, list[str]]:
    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    settings = get_settings()
    try:
        payload = decode_access_token(credentials.credentials, settings.auth_secret_key)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token") from exc

    username = str(payload["sub"])
    user = get_user_by_username(db, username)
    if user is None or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    roles = get_user_roles(db, user.id)
    return user, roles


def require_roles(*required_roles: str) -> Callable:
    def dependency(context: tuple[User, list[str]] = Depends(get_current_user_context)) -> tuple[User, list[str]]:
        user, roles = context
        if not user_has_any_role(roles, required_roles):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
        return user, roles

    return dependency
