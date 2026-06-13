import importlib
import os
import tempfile
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from httpx import ASGITransport, AsyncClient


class EngineAdminApiTestCaseMixin:
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "engine_admin_test.db"

        os.environ["APP_ENV"] = "test"
        os.environ["DATABASE_URL"] = f"sqlite+pysqlite:///{self.db_path.as_posix()}"
        os.environ["AUTH_SECRET_KEY"] = "test-secret-key"

        from backend.app.config.settings import clear_settings_cache
        from backend.app.infrastructure.db.session import clear_database_caches

        clear_settings_cache()
        clear_database_caches()

        from backend.app.infrastructure.db.base import Base
        from backend.app.infrastructure.db.models import Role, User, UserRole
        from backend.app.infrastructure.db.session import get_engine, get_session_factory
        from backend.app.security.passwords import hash_password

        engine = get_engine()
        session_factory = get_session_factory()

        Base.metadata.create_all(bind=engine)

        self._users_by_username: dict[str, str] = {}

        with session_factory() as session:
            role_codes = ("admin", "admin_negocio", "admin_riesgos", "admin_plataforma", "auditor")
            roles = {
                code: Role(
                    id=str(uuid4()),
                    code=code,
                    name=code,
                    created_at=datetime.now(UTC),
                )
                for code in role_codes
            }
            users = {
                username: User(
                    id=str(uuid4()),
                    username=username,
                    display_name=username,
                    password_hash=hash_password("secret123"),
                    is_active=True,
                    created_at=datetime.now(UTC),
                )
                for username in (
                    "admin",
                    "negocio",
                    "riesgos",
                    "plataforma",
                    "auditor",
                )
            }

            role_by_user = {
                "admin": "admin",
                "negocio": "admin_negocio",
                "riesgos": "admin_riesgos",
                "plataforma": "admin_plataforma",
                "auditor": "auditor",
            }

            session.add_all([*roles.values(), *users.values()])
            session.flush()
            session.add_all(
                [
                    UserRole(
                        id=str(uuid4()),
                        user_id=users[username].id,
                        role_id=roles[role_code].id,
                        created_at=datetime.now(UTC),
                    )
                    for username, role_code in role_by_user.items()
                ]
            )
            session.commit()

            self._users_by_username = {username: user.id for username, user in users.items()}

    def tearDown(self):
        from backend.app.config.settings import clear_settings_cache
        from backend.app.infrastructure.db.session import clear_database_caches

        clear_settings_cache()
        clear_database_caches()
        self.temp_dir.cleanup()

    def get_app(self):
        import backend.app.main as main_module

        return importlib.reload(main_module).app

    async def login(self, client: AsyncClient, username: str) -> str:
        response = await client.post(
            "/api/v1/auth/login",
            json={"username": username, "password": "secret123"},
        )
        assert response.status_code == 200, response.text
        return response.json()["access_token"]

    async def auth_headers(self, client: AsyncClient, username: str) -> dict[str, str]:
        token = await self.login(client, username)
        return {"Authorization": f"Bearer {token}"}

    def build_transport(self) -> ASGITransport:
        return ASGITransport(app=self.get_app())
