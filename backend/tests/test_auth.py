import asyncio
import os
import sys
import tempfile
import unittest
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from httpx import ASGITransport, AsyncClient


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


class AuthenticationTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "auth_test.db"

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

        with session_factory() as session:
            admin_role = Role(
                id=str(uuid4()),
                code="admin",
                name="Administrador",
                created_at=datetime.now(UTC),
            )
            analyst_role = Role(
                id=str(uuid4()),
                code="analista",
                name="Analista",
                created_at=datetime.now(UTC),
            )
            admin_user = User(
                id=str(uuid4()),
                username="admin",
                display_name="Admin User",
                password_hash=hash_password("secret123"),
                is_active=True,
                created_at=datetime.now(UTC),
            )
            analyst_user = User(
                id=str(uuid4()),
                username="analista",
                display_name="Analyst User",
                password_hash=hash_password("secret123"),
                is_active=True,
                created_at=datetime.now(UTC),
            )

            session.add_all([admin_role, analyst_role, admin_user, analyst_user])
            session.flush()
            session.add_all(
                [
                    UserRole(
                        id=str(uuid4()),
                        user_id=admin_user.id,
                        role_id=admin_role.id,
                        created_at=datetime.now(UTC),
                    ),
                    UserRole(
                        id=str(uuid4()),
                        user_id=analyst_user.id,
                        role_id=analyst_role.id,
                        created_at=datetime.now(UTC),
                    ),
                ]
            )
            session.commit()

    def tearDown(self):
        from backend.app.infrastructure.db.session import clear_database_caches

        clear_database_caches()
        self.temp_dir.cleanup()

    def test_login_returns_bearer_token_and_me(self):
        from backend.app.main import app

        async def run_test():
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://testserver") as client:
                login_response = await client.post(
                    "/api/v1/auth/login",
                    json={"username": "admin", "password": "secret123"},
                )

                self.assertEqual(login_response.status_code, 200)
                payload = login_response.json()
                self.assertEqual(payload["token_type"], "bearer")
                self.assertIn("access_token", payload)

                me_response = await client.get(
                    "/api/v1/me",
                    headers={"Authorization": f"Bearer {payload['access_token']}"},
                )

                self.assertEqual(me_response.status_code, 200)
                self.assertEqual(
                    me_response.json(),
                    {
                        "id": me_response.json()["id"],
                        "username": "admin",
                        "display_name": "Admin User",
                        "roles": ["admin"],
                        "authorization_mode": "request_time",
                    },
                )

        asyncio.run(run_test())

    def test_login_rejects_invalid_credentials(self):
        from backend.app.main import app

        async def run_test():
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://testserver") as client:
                response = await client.post(
                    "/api/v1/auth/login",
                    json={"username": "admin", "password": "wrong"},
                )

                self.assertEqual(response.status_code, 401)
                self.assertEqual(response.json()["detail"], "Invalid credentials")

        asyncio.run(run_test())

    def test_admin_route_requires_admin_role(self):
        from backend.app.main import app

        async def run_test():
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://testserver") as client:
                login_response = await client.post(
                    "/api/v1/auth/login",
                    json={"username": "analista", "password": "secret123"},
                )
                token = login_response.json()["access_token"]

                forbidden_response = await client.get(
                    "/api/v1/admin/health",
                    headers={"Authorization": f"Bearer {token}"},
                )
                self.assertEqual(forbidden_response.status_code, 403)

                admin_login = await client.post(
                    "/api/v1/auth/login",
                    json={"username": "admin", "password": "secret123"},
                )
                admin_token = admin_login.json()["access_token"]

                ok_response = await client.get(
                    "/api/v1/admin/health",
                    headers={"Authorization": f"Bearer {admin_token}"},
                )
                self.assertEqual(ok_response.status_code, 200)
                self.assertEqual(ok_response.json()["status"], "ok")

        asyncio.run(run_test())


if __name__ == "__main__":
    unittest.main()
