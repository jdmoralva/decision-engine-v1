import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


class EvaluationContractMapperTests(unittest.TestCase):
    def test_api_request_maps_to_engine_request_without_http_types(self):
        from backend.app.api.mappers.evaluations import map_api_request_to_engine_request
        from backend.app.api.schemas.contracts import PLDEvaluationRequest

        api_request = PLDEvaluationRequest(
            product_code="PLD",
            workflow_code="standard",
            document={"document_type": "DNI", "document_number": "12345678"},
            requested_by={"username": "analista", "user_id": "u-1"},
            product_context={
                "campaign_code": "PLD-01",
                "customer_type": "docente",
                "validated_income": 1800,
            },
            requested_rule_set_version="rules-v2",
            requested_pipeline_version="pipe-v3",
            external_inputs=[
                {
                    "source_type": "customer",
                    "source_key": "doc:12345678",
                    "field_name": "segment_code",
                    "field_value": "PREFERENTIAL",
                }
            ],
        )

        engine_request = map_api_request_to_engine_request(api_request)

        self.assertEqual(engine_request.product_code, "PLD")
        self.assertEqual(engine_request.workflow_code, "standard")
        self.assertEqual(engine_request.requested_rule_set_version, "rules-v2")
        self.assertEqual(engine_request.requested_pipeline_version, "pipe-v3")
        self.assertEqual(engine_request.document.document_number, "12345678")
        self.assertEqual(engine_request.requested_by.user_id, "u-1")
        self.assertEqual(engine_request.product_context["campaign_code"], "PLD-01")
        self.assertEqual(engine_request.product_context["validated_income"], 1800.0)
        self.assertNotIn("reported_debt", engine_request.product_context)

    def test_engine_result_maps_to_rest_response_with_pld_projection(self):
        from backend.app.api.mappers.evaluations import map_engine_result_to_api_response
        from backend.app.domain.decision_engine import (
            AppliedVersions,
            EngineDecisionTrace,
            EngineEvaluationResult,
        )

        engine_result = EngineEvaluationResult(
            product_code="PLD",
            eligible=True,
            alerts=["manual_review"],
            blocks=[],
            applied_versions=AppliedVersions(
                rule_set_version="rules-v1",
                parameter_version="params-v1",
                pipeline_version="pipe-v1",
            ),
            product_result={
                "segment_code": "A1",
                "reviewed_income": 2100.5,
                "rci": 0.32,
                "offered_amount": 5000,
                "installment_amount": 280.4,
                "rate": 0.18,
                "term_months": 24,
                "internal_score": 900,
            },
            decision_trace=EngineDecisionTrace(product_code="PLD", workflow_code="standard"),
        )

        response = map_engine_result_to_api_response(
            evaluation_id="eval-1",
            engine_result=engine_result,
        )

        self.assertEqual(response.evaluation_id, "eval-1")
        self.assertEqual(response.product_code, "PLD")
        self.assertEqual(response.decision_trace_id, engine_result.decision_trace.trace_id)
        self.assertEqual(response.product_result.segment_code, "A1")
        self.assertEqual(response.product_result.term_months, 24)

    def test_engine_result_keeps_non_pld_response_generic(self):
        from backend.app.api.mappers.evaluations import map_engine_result_to_api_response
        from backend.app.domain.decision_engine import EngineDecisionTrace, EngineEvaluationResult

        engine_result = EngineEvaluationResult(
            product_code="AUTO",
            eligible=False,
            alerts=[],
            blocks=["rule_blocked"],
            product_result={"lvr": 0.7},
            decision_trace=EngineDecisionTrace(product_code="AUTO", workflow_code="standard"),
        )

        response = map_engine_result_to_api_response(
            evaluation_id="eval-2",
            engine_result=engine_result,
        )

        self.assertEqual(response.product_code, "AUTO")
        self.assertIsNone(response.product_result)
        self.assertEqual(response.blocks, ["rule_blocked"])

    def test_engine_trace_maps_to_rest_trace_response(self):
        from backend.app.api.mappers.evaluations import map_engine_trace_to_api_response
        from backend.app.domain.decision_engine import (
            AppliedVersions,
            EngineDecisionEvidence,
            EngineDecisionTrace,
            EngineDecisionTraceNode,
        )

        trace = EngineDecisionTrace(
            product_code="PLD",
            workflow_code="standard",
            applied_versions=AppliedVersions(pipeline_version="pipe-v1"),
            alerts=["manual_review"],
            blocks=[],
            nodes_executed=[
                EngineDecisionTraceNode(
                    node_key="eligibility",
                    node_type="eligibility",
                    outcome="eligible",
                    branch_selected="offer",
                    rules_applied=["rule-eligibility"],
                    consumed_variables=["campaign_code"],
                    produced_variables=["segment_code"],
                    produced_effects=["manual_review"],
                )
            ],
            evidence=[
                EngineDecisionEvidence(
                    source_type="customer",
                    source_key="doc:12345678",
                    field_name="segment_code",
                    field_value="A1",
                )
            ],
            rules_applied=["rule-eligibility"],
            consumed_variables=["campaign_code"],
            produced_variables=["segment_code"],
            produced_effects=["manual_review"],
        )

        response = map_engine_trace_to_api_response(
            evaluation_id="eval-3",
            engine_trace=trace,
        )

        self.assertEqual(response.trace_id, trace.trace_id)
        self.assertEqual(response.evaluation_id, "eval-3")
        self.assertEqual(response.nodes_executed[0].node_key, "eligibility")
        self.assertEqual(response.nodes_executed[0].rules_applied, ["rule-eligibility"])
        self.assertEqual(response.nodes_executed[0].consumed_variables, ["campaign_code"])
        self.assertEqual(response.nodes_executed[0].produced_variables, ["segment_code"])
        self.assertEqual(response.nodes_executed[0].produced_effects, ["manual_review"])
        self.assertEqual(response.rules_applied, ["rule-eligibility"])
        self.assertEqual(response.consumed_variables, ["campaign_code"])
        self.assertEqual(response.produced_variables, ["segment_code"])
        self.assertEqual(response.produced_effects, ["manual_review"])
        self.assertEqual(response.evidence[0].field_name, "segment_code")
