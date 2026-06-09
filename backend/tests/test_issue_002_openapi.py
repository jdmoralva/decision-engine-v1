import asyncio
import sys
import unittest
from pathlib import Path

from httpx import ASGITransport, AsyncClient


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


class Issue002OpenAPITests(unittest.TestCase):
    def test_openapi_exposes_contract_resources_and_shared_schemas(self):
        from backend.app.main import app

        async def run_request():
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://testserver") as client:
                return await client.get("/openapi.json")

        response = asyncio.run(run_request())

        self.assertEqual(response.status_code, 200)
        payload = response.json()

        self.assertIn("/api/v1/evaluations", payload["paths"])
        self.assertIn("/api/v1/evaluations/{evaluation_id}", payload["paths"])
        self.assertIn("/api/v1/evaluations/{evaluation_id}/decision-trace", payload["paths"])
        self.assertIn("/api/v1/credit-requests", payload["paths"])
        self.assertIn("/api/v1/credit-requests/{request_id}", payload["paths"])
        self.assertIn(
            "/api/v1/credit-requests/{request_id}/status-transitions",
            payload["paths"],
        )

        schemas = payload["components"]["schemas"]

        for schema_name in (
            "EvaluationRequest",
            "EvaluationResponse",
            "DecisionTraceResponse",
            "CreditRequestCreateRequest",
            "CreditRequestResponse",
            "CreditRequestStatusTransitionRequest",
            "StructuredErrorResponse",
            "DocumentRef",
            "ActorRef",
            "ExternalInputSnapshotItem",
            "PLDEvaluationContext",
            "PLDEvaluationResult",
        ):
            self.assertIn(schema_name, schemas)

        evaluation_request = schemas["EvaluationRequest"]
        self.assertEqual(
            evaluation_request["required"],
            ["product_code", "document", "requested_by", "product_context"],
        )
        self.assertIn("product_context", evaluation_request["properties"])
        self.assertNotIn("rci", evaluation_request["properties"])
        self.assertNotIn("marca_sunedu", evaluation_request["properties"])

        evaluation_response = schemas["EvaluationResponse"]
        self.assertIn("product_result", evaluation_response["properties"])
        self.assertNotIn("rci", evaluation_response["properties"])

        error_schema = schemas["StructuredErrorResponse"]
        self.assertEqual(error_schema["required"], ["error"])


if __name__ == "__main__":
    unittest.main()
