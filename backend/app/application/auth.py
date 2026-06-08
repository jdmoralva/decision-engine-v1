from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.infrastructure.db.models import Role, User, UserRole
from backend.app.security.passwords import verify_password


def get_user_by_username(db: Session, username: str) -> User | None:
    return db.execute(select(User).where(User.username == username)).scalar_one_or_none()


def get_user_roles(db: Session, user_id: str) -> list[str]:
    query = (
        select(Role.code)
        .join(UserRole, UserRole.role_id == Role.id)
        .where(UserRole.user_id == user_id)
        .order_by(Role.code)
    )
    return list(db.execute(query).scalars().all())


def authenticate_user(db: Session, username: str, password: str) -> tuple[User, list[str]] | None:
    user = get_user_by_username(db, username)
    if user is None or not user.is_active:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user, get_user_roles(db, user.id)


def user_has_any_role(user_roles: Sequence[str], required_roles: Sequence[str]) -> bool:
    return any(role in required_roles for role in user_roles)
