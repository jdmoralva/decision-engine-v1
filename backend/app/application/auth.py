from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.infrastructure.db.models import Permission, Role, RolePermission, User, UserRole
from backend.app.security.passwords import verify_password
from backend.app.security.permissions import ROLE_PERMISSIONS


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


def get_permissions_for_roles(db: Session, role_codes: Sequence[str]) -> set[str]:
    if not role_codes:
        return set()

    persisted_rows = db.execute(
        select(Role.code, Permission.code)
        .join(RolePermission, RolePermission.role_id == Role.id)
        .join(Permission, Permission.id == RolePermission.permission_id)
        .where(Role.code.in_(role_codes))
    ).all()

    persisted_by_role: dict[str, set[str]] = {}
    for role_code, permission_code in persisted_rows:
        persisted_by_role.setdefault(role_code, set()).add(permission_code)

    resolved_permissions: set[str] = set()
    for role_code in role_codes:
        role_permissions = persisted_by_role.get(role_code)
        if role_permissions is None:
            resolved_permissions.update(ROLE_PERMISSIONS.get(role_code, set()))
            continue
        resolved_permissions.update(role_permissions)

    return resolved_permissions


def authenticate_user(db: Session, username: str, password: str) -> tuple[User, list[str]] | None:
    user = get_user_by_username(db, username)
    if user is None or not user.is_active:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user, get_user_roles(db, user.id)


def user_has_any_role(user_roles: Sequence[str], required_roles: Sequence[str]) -> bool:
    return any(role in required_roles for role in user_roles)
