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


class RBACPermissionTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "rbac_test.db"

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
            roles = {
                code: Role(
                    id=str(uuid4()),
                    code=code,
                    name=code.capitalize(),
                    created_at=datetime.now(UTC),
                )
                for code in ("admin", "analista", "evaluador", "supervisor")
            }
            users = {
                username: User(
                    id=str(uuid4()),
                    username=username,
                    display_name=username.capitalize(),
                    password_hash=hash_password("secret123"),
                    is_active=True,
                    created_at=datetime.now(UTC),
                )
                for username in ("admin", "analista", "evaluador", "supervisor")
            }

            session.add_all([*roles.values(), *users.values()])
            session.flush()
            session.add_all(
                [
                    UserRole(
                        id=str(uuid4()),
                        user_id=users[code].id,
                        role_id=roles[code].id,
                        created_at=datetime.now(UTC),
                    )
                    for code in roles
                ]
            )
            session.commit()

    def tearDown(self):
        from backend.app.infrastructure.db.session import clear_database_caches

        clear_database_caches()
        self.temp_dir.cleanup()

    async def _login(self, client: AsyncClient, username: str) -> str:
        response = await client.post(
            "/api/v1/auth/login",
            json={"username": username, "password": "secret123"},
        )
        self.assertEqual(response.status_code, 200)
        return response.json()["access_token"]

    def test_analista_cannot_consult_decision_trace(self):
        from backend.app.main import app

        async def run_test():
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://testserver") as client:
                token = await self._login(client, "analista")
                response = await client.get(
                    "/api/v1/evaluations/example-evaluation/decision-trace",
                    headers={"Authorization": f"Bearer {token}"},
                )
                self.assertEqual(response.status_code, 403)

        asyncio.run(run_test())

    def test_evaluador_can_consult_decision_trace(self):
        from backend.app.main import app

        async def run_test():
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://testserver") as client:
                token = await self._login(client, "evaluador")
                response = await client.get(
                    "/api/v1/evaluations/example-evaluation/decision-trace",
                    headers={"Authorization": f"Bearer {token}"},
                )
                self.assertEqual(response.status_code, 501)

        asyncio.run(run_test())

    def test_evaluador_cannot_register_credit_request(self):
        from backend.app.main import app

        async def run_test():
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://testserver") as client:
                token = await self._login(client, "evaluador")
                response = await client.post(
                    "/api/v1/credit-requests",
                    headers={"Authorization": f"Bearer {token}"},
                    json={
                        "product_code": "PLD",
                        "document": {"document_type": "DNI", "document_number": "12345678"},
                        "requested_amount": 1000,
                        "comment": "test",
                        "created_by": {"username": "evaluador"},
                    },
                )
                self.assertEqual(response.status_code, 403)

        asyncio.run(run_test())

    def test_analista_can_register_credit_request(self):
        from backend.app.main import app

        async def run_test():
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://testserver") as client:
                token = await self._login(client, "analista")
                response = await client.post(
                    "/api/v1/credit-requests",
                    headers={"Authorization": f"Bearer {token}"},
                    json={
                        "product_code": "PLD",
                        "document": {"document_type": "DNI", "document_number": "12345678"},
                        "requested_amount": 1000,
                        "comment": "test",
                        "created_by": {"username": "analista"},
                    },
                )
                self.assertEqual(response.status_code, 501)

        asyncio.run(run_test())

    def test_analista_cannot_change_credit_request_status(self):
        from backend.app.main import app

        async def run_test():
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://testserver") as client:
                token = await self._login(client, "analista")
                response = await client.post(
                    "/api/v1/credit-requests/example-request/status-transitions",
                    headers={"Authorization": f"Bearer {token}"},
                    json={"target_status": "approved", "changed_by": {"username": "analista"}},
                )
                self.assertEqual(response.status_code, 403)

        asyncio.run(run_test())

    def test_supervisor_can_change_credit_request_status(self):
        from backend.app.main import app

        async def run_test():
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://testserver") as client:
                token = await self._login(client, "supervisor")
                response = await client.post(
                    "/api/v1/credit-requests/example-request/status-transitions",
                    headers={"Authorization": f"Bearer {token}"},
                    json={"target_status": "approved", "changed_by": {"username": "supervisor"}},
                )
                self.assertEqual(response.status_code, 501)

        asyncio.run(run_test())

    def test_analista_can_cancel_credit_request(self):
        from backend.app.main import app

        async def run_test():
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://testserver") as client:
                token = await self._login(client, "analista")
                response = await client.post(
                    "/api/v1/credit-requests/example-request/status-transitions",
                    headers={"Authorization": f"Bearer {token}"},
                    json={"target_status": "cancelled", "changed_by": {"username": "analista"}},
                )
                self.assertEqual(response.status_code, 501)

        asyncio.run(run_test())

    def test_cancel_credit_request_requires_authentication(self):
        from backend.app.main import app

        async def run_test():
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://testserver") as client:
                response = await client.post(
                    "/api/v1/credit-requests/example-request/status-transitions",
                    json={"target_status": "cancelled", "changed_by": {"username": "analista"}},
                )
                self.assertEqual(response.status_code, 401)

        asyncio.run(run_test())

    def test_analista_cannot_access_rule_administration(self):
        from backend.app.main import app

        async def run_test():
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://testserver") as client:
                token = await self._login(client, "analista")
                response = await client.get(
                    "/api/v1/admin/rules",
                    headers={"Authorization": f"Bearer {token}"},
                )
                self.assertEqual(response.status_code, 403)

        asyncio.run(run_test())

    def test_admin_can_access_rule_administration(self):
        from backend.app.main import app

        async def run_test():
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://testserver") as client:
                token = await self._login(client, "admin")
                response = await client.get(
                    "/api/v1/admin/rules",
                    headers={"Authorization": f"Bearer {token}"},
                )
                self.assertEqual(response.status_code, 501)

        asyncio.run(run_test())


if __name__ == "__main__":
    unittest.main()
