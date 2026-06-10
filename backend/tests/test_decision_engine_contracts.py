import sys
import unittest
from pathlib import Path

from pydantic import ValidationError

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


class DecisionEngineContractTests(unittest.TestCase):
    def test_domain_package_exports_engine_contracts_without_fastapi_dependency(self):
        from backend.app.domain.decision_engine import (
            AppliedVersions,
            EngineActorRef,
            EngineDocumentRef,
            EngineEvaluationRequest,
            EngineExternalInput,
        )

        document = EngineDocumentRef(document_type="dni", document_number="12345678")
        external_input = EngineExternalInput(
            source_type="customer",
            source_key="doc:1",
            field_name="age",
            field_value="42",
        )

        self.assertEqual(document.document_type, "dni")
        self.assertEqual(EngineActorRef(username="analista").username, "analista")
        self.assertEqual(AppliedVersions().pipeline_version, None)
        self.assertEqual(external_input.field_name, "age")
        self.assertEqual(
            EngineEvaluationRequest.model_fields["product_context"].annotation,
            dict[str, object],
        )

    def test_engine_request_requires_shared_fields_only(self):
        from backend.app.domain.decision_engine import EngineEvaluationRequest

        payload = EngineEvaluationRequest(
            product_code="pld",
            document={"document_type": "dni", "document_number": "12345678"},
            requested_by={"username": "analista"},
            product_context={"campaign_code": "PLD-01"},
        )

        self.assertEqual(payload.product_code, "pld")
        self.assertEqual(payload.product_context, {"campaign_code": "PLD-01"})

    def test_engine_request_rejects_missing_product_context(self):
        from backend.app.domain.decision_engine import EngineEvaluationRequest

        with self.assertRaises(ValidationError):
            EngineEvaluationRequest(
                product_code="pld",
                document={"document_type": "dni", "document_number": "12345678"},
                requested_by={"username": "analista"},
            )
