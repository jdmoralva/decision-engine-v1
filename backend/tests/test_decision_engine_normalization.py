import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


from backend.app.domain.decision_engine import (  # noqa: E402
    EngineEvaluationRequest,
    EngineValidationError,
    normalize_evaluation_request,
)


class DecisionEngineNormalizationTests(unittest.TestCase):
    def test_normalize_request_trims_and_uppercases_shared_identifiers(self):
        request = EngineEvaluationRequest(
            product_code="  auto  ",
            workflow_code=" standard  ",
            document={"document_type": " dni ", "document_number": " 12345678 "},
            requested_by={"username": " analista "},
            product_context={"campaign_code": "AUTO-01"},
            external_inputs=[
                {
                    "source_type": " customer ",
                    "source_key": " doc:12345678 ",
                    "field_name": " segment ",
                    "field_value": " preferred ",
                }
            ],
        )

        normalized = normalize_evaluation_request(request)

        self.assertEqual(normalized.product_code, "AUTO")
        self.assertEqual(normalized.workflow_code, "standard")
        self.assertEqual(normalized.document.document_type, "DNI")
        self.assertEqual(normalized.document.document_number, "12345678")
        self.assertEqual(normalized.requested_by.username, "analista")
        self.assertEqual(normalized.external_inputs[0].source_type, "customer")
        self.assertEqual(normalized.external_inputs[0].source_key, "doc:12345678")
        self.assertEqual(normalized.external_inputs[0].field_name, "segment")
        self.assertEqual(normalized.external_inputs[0].field_value, "preferred")

    def test_normalize_request_rejects_blank_product_code(self):
        request = EngineEvaluationRequest(
            product_code="   ",
            workflow_code="standard",
            document={"document_type": "dni", "document_number": "12345678"},
            requested_by={"username": "analista"},
            product_context={},
        )

        with self.assertRaises(EngineValidationError):
            normalize_evaluation_request(request)

    def test_normalize_request_rejects_blank_workflow_code(self):
        request = EngineEvaluationRequest(
            product_code="AUTO",
            workflow_code="   ",
            document={"document_type": "dni", "document_number": "12345678"},
            requested_by={"username": "analista"},
            product_context={},
        )

        with self.assertRaises(EngineValidationError):
            normalize_evaluation_request(request)
