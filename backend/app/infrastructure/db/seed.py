from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.infrastructure.db.base import Base
from backend.app.infrastructure.db.models import Role, User, UserRole
from backend.app.infrastructure.db.session import get_engine, get_session_factory
from backend.app.security.passwords import hash_password


DEFAULT_ROLES = [
    ("admin", "Administrador"),
    ("analista", "Analista"),
    ("evaluador", "Evaluador"),
    ("auditor", "Auditor"),
    ("admin_negocio", "Administrador de negocio"),
    ("admin_riesgos", "Administrador de riesgos"),
    ("plataforma", "Administracion privilegiada de plataforma"),
]

DEFAULT_USERS = [
    ("admin", "Administrador", "admin123", "admin"),
    ("analista", "Analista", "analista123", "analista"),
    ("evaluador", "Evaluador", "evaluador123", "evaluador"),
    ("auditor", "Auditor", "auditor123", "auditor"),
    ("negocio", "Administrador Negocio", "negocio123", "admin_negocio"),
    ("riesgos", "Administrador Riesgos", "riesgos123", "admin_riesgos"),
    ("plataforma", "Administrador Plataforma", "plataforma123", "plataforma"),
]


def seed_identity_data(session: Session) -> dict[str, int]:
    now = datetime.now(UTC)
    roles_created = 0
    users_created = 0

    existing_roles = {
        role.code: role
        for role in session.execute(select(Role)).scalars().all()
    }

    for code, name in DEFAULT_ROLES:
        if code not in existing_roles:
            role = Role(id=str(uuid4()), code=code, name=name, created_at=now)
            session.add(role)
            existing_roles[code] = role
            roles_created += 1

    session.flush()

    existing_users = {
        user.username: user
        for user in session.execute(select(User)).scalars().all()
    }
    existing_user_roles = {
        (user_role.user_id, user_role.role_id)
        for user_role in session.execute(select(UserRole)).scalars().all()
    }

    for username, display_name, password, role_code in DEFAULT_USERS:
        user = existing_users.get(username)
        if user is None:
            user = User(
                id=str(uuid4()),
                username=username,
                display_name=display_name,
                password_hash=hash_password(password),
                is_active=True,
                created_at=now,
            )
            session.add(user)
            session.flush()
            existing_users[username] = user
            users_created += 1

        role = existing_roles[role_code]
        relation_key = (user.id, role.id)
        if relation_key not in existing_user_roles:
            session.add(
                UserRole(
                    id=str(uuid4()),
                    user_id=user.id,
                    role_id=role.id,
                    created_at=now,
                )
            )
            existing_user_roles.add(relation_key)

    session.commit()
    return {"roles_created": roles_created, "users_created": users_created}


def seed_identity_data_for_local_dev() -> dict[str, int]:
    engine = get_engine()
    Base.metadata.create_all(bind=engine)

    session_factory = get_session_factory()
    with session_factory() as session:
        return seed_identity_data(session)


if __name__ == "__main__":
    result = seed_identity_data_for_local_dev()
    print(
        "Seed complete: "
        f"roles_created={result['roles_created']}, "
        f"users_created={result['users_created']}"
    )
