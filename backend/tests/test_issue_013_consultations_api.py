import asyncio
import os
import sys
import tempfile
import unittest

from pathlib import Path

from httpx import ASGITransport, AsyncClient


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


class Issue013ConsultationsApiTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "issue_013.db"

        os.environ["APP_ENV"] = "test"
        os.environ["DATABASE_URL"] = f"sqlite+pysqlite:///{self.db_path.as_posix()}"
        os.environ["AUTH_SECRET_KEY"] = "test-secret-key"

        from backend.app.config.settings import clear_settings_cache
        from backend.app.infrastructure.db.session import clear_database_caches

        clear_settings_cache()
        clear_database_caches()

        from backend.app.infrastructure.db.base import Base
        from backend.app.infrastructure.db.models import LoanProduct
        from backend.app.infrastructure.db.seed import seed_identity_data
        from backend.app.infrastructure.db.session import get_engine, get_session_factory
        from datetime import UTC, datetime

        engine = get_engine()
        session_factory = get_session_factory()

        Base.metadata.create_all(bind=engine)

        with session_factory() as session:
            seed_identity_data(session)
            session.add(
                LoanProduct(
                    code="PLD",
                    name="Prestamo de Libre Disponibilidad",
                    is_active=True,
                    created_at=datetime.now(UTC),
                )
            )
            session.commit()

    def tearDown(self):
        from backend.app.infrastructure.db.session import clear_database_caches

        clear_database_caches()
        self.temp_dir.cleanup()

    async def _login(self, client: AsyncClient, username: str) -> str:
        response = await client.post(
            "/api/v1/auth/login",
            json={"username": username, "password": f"{username}123"},
        )
        self.assertEqual(response.status_code, 200)
        return response.json()["access_token"]

    def test_openapi_exposes_loans_consultations_endpoint_and_schemas(self):
        from backend.app.main import app

        async def run_request():
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://testserver") as client:
                return await client.get("/openapi.json")

        response = asyncio.run(run_request())

        self.assertEqual(response.status_code, 200)
        payload = response.json()

        self.assertIn("/api/v1/loans/{product_code}/consultas", payload["paths"])

        schemas = payload["components"]["schemas"]
        for schema_name in (
            "LoanConsultationRequest",
            "LoanConsultationResponse",
            "LoanConsultationCustomer",
            "LoanConsultationCampaign",
        ):
            self.assertIn(schema_name, schemas)

    def test_analista_can_consult_customer_campaigns_for_supported_product(self):
        from backend.app.main import app

        async def run_test():
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://testserver") as client:
                token = await self._login(client, "analista")
                response = await client.post(
                    "/api/v1/loans/PLD/consultas",
                    headers={"Authorization": f"Bearer {token}"},
                    json={"document": {"document_type": "DNI", "document_number": "12345678"}},
                )

                self.assertEqual(response.status_code, 200)
                payload = response.json()
                self.assertEqual(payload["product_code"], "PLD")
                self.assertEqual(payload["document"], {"document_type": "DNI", "document_number": "12345678"})
                self.assertEqual(payload["customer"]["customer_type"], "CLIENTE")
                self.assertGreaterEqual(len(payload["campaigns"]), 1)
                self.assertEqual(payload["campaigns"][0]["campaign_code"], "PLD_48M")

        asyncio.run(run_test())

    def test_consultation_requires_authentication(self):
        from backend.app.main import app

        async def run_test():
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://testserver") as client:
                response = await client.post(
                    "/api/v1/loans/PLD/consultas",
                    json={"document": {"document_type": "DNI", "document_number": "12345678"}},
                )

                self.assertEqual(response.status_code, 401)
                self.assertEqual(
                    response.json(),
                    {
                        "error": {
                            "code": "AUTHENTICATION_REQUIRED",
                            "message": "Not authenticated",
                            "details": [],
                        }
                    },
                )

        asyncio.run(run_test())

    def test_consultation_rejects_unknown_product(self):
        from backend.app.main import app

        async def run_test():
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://testserver") as client:
                token = await self._login(client, "analista")
                response = await client.post(
                    "/api/v1/loans/XYZ/consultas",
                    headers={"Authorization": f"Bearer {token}"},
                    json={"document": {"document_type": "DNI", "document_number": "12345678"}},
                )

                self.assertEqual(response.status_code, 404)
                self.assertEqual(response.json()["error"]["code"], "LOAN_PRODUCT_NOT_AVAILABLE")

        asyncio.run(run_test())


if __name__ == "__main__":
    unittest.main()
