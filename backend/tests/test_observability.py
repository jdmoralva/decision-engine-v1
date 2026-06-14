import asyncio
import logging
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

from httpx import AsyncClient

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.app.application.ai.exceptions import AIServiceError
from backend.app.application.ai.evaluation_explanations import EvaluationExplanationService
from backend.app.domain.decision_engine.contracts import (
    AppliedVersions,
    EngineActorRef,
    EngineDecisionTrace,
    EngineDocumentRef,
    EngineEvaluationRequest,
    EngineEvaluationResult,
)
from backend.tests.runtime_test_support import RuntimeApiTestCaseMixin


class _RecordingRepository:
    def __init__(self) -> None:
        self.records = []

    def create(self, data) -> None:
        self.records.append(data)


class ObservabilityIntegrationTests(RuntimeApiTestCaseMixin, unittest.TestCase):
    def test_request_id_header_is_echoed_on_successful_requests(self):
        async def run_test():
            async with AsyncClient(transport=self.build_transport(), base_url="http://testserver") as client:
                response = await client.get(
                    "/api/v1/health",
                    headers={"X-Request-ID": "req-observability-001"},
                )

            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.headers.get("X-Request-ID"), "req-observability-001")

        asyncio.run(run_test())


class EvaluationExplanationObservabilityTests(unittest.TestCase):
    def test_ai_fallback_logs_degradation_with_request_context(self):
        repository = _RecordingRepository()
        service = EvaluationExplanationService(repository)
        request = EngineEvaluationRequest(
            product_code="PLD",
            workflow_code="standard",
            document=EngineDocumentRef(document_type="DNI", document_number="12345678"),
            requested_by=EngineActorRef(user_id="user-1", username="analista"),
            product_context={"campaign_code": "PLD_48M", "validated_income": 2500},
            external_inputs=[],
        )
        result = EngineEvaluationResult(
            product_code="PLD",
            eligible=True,
            alerts=[],
            blocks=[],
            product_result={"offered_amount": 12000},
            applied_versions=AppliedVersions(
                parameter_version="param-v1",
                pipeline_version="pipe-v1",
                rule_set_version="rule-v1",
            ),
            decision_trace=EngineDecisionTrace(product_code="PLD", workflow_code="standard"),
        )

        from backend.app.application.observability import request_context

        with request_context("req-observability-002"):
            with patch(
                "backend.app.application.ai.evaluation_explanations.build_ai_model_client",
                side_effect=AIServiceError("provider down"),
            ):
                with self.assertLogs("decision_engine.ai", level=logging.WARNING) as captured:
                    summary = asyncio.run(
                        service.summarize(
                            evaluation_id="eval-1",
                            actor_user_id="user-1",
                            request=request,
                            result=result,
                        )
                    )

        self.assertIn("offered_amount=12000", summary)
        self.assertEqual(len(repository.records), 1)
        self.assertTrue(any("req-observability-002" in message for message in captured.output))
        self.assertTrue(any("ai_degraded" in message for message in captured.output))
