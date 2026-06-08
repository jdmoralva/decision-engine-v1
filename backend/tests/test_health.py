import asyncio
import os
import sys
import unittest
from pathlib import Path

from httpx import ASGITransport, AsyncClient


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


class HealthEndpointTests(unittest.TestCase):
    def test_health_endpoint_reports_ok_and_environment(self):
        os.environ["APP_ENV"] = "test"

        from backend.app.main import app

        async def run_request():
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://testserver") as client:
                return await client.get("/api/v1/health")

        response = asyncio.run(run_request())

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                "status": "ok",
                "service": "decision-engine-api",
                "environment": "test",
            },
        )


if __name__ == "__main__":
    unittest.main()
