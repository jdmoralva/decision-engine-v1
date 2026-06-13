import sys
import unittest
from pathlib import Path

from sqlalchemy import create_engine, inspect


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


class ModelMetadataTests(unittest.TestCase):
    def test_metadata_contains_core_mvp_tables(self):
        from backend.app.infrastructure.db.base import Base
        from backend.app.infrastructure.db import models  # noqa: F401

        expected_tables = {
            "users",
            "roles",
            "user_roles",
            "loan_products",
            "product_workflows",
            "workflow_versions",
            "product_variables",
            "variable_catalog_versions",
            "variable_catalog_items",
            "parameter_sets",
            "workflow_rule_assignments",
            "credit_requests",
            "credit_request_status_history",
            "credit_request_attachments",
            "loan_evaluations",
            "evaluation_input_snapshots",
            "decision_traces",
            "decision_events",
            "administrative_audit_events",
            "rule_sets",
            "rule_versions",
            "pipeline_strategies",
            "pipeline_nodes",
            "ai_interactions",
            "ai_prompt_templates",
        }

        self.assertTrue(expected_tables.issubset(Base.metadata.tables.keys()))

    def test_core_tables_create_in_sqlite(self):
        from backend.app.infrastructure.db.base import Base
        from backend.app.infrastructure.db import models  # noqa: F401

        engine = create_engine("sqlite+pysqlite:///:memory:")
        Base.metadata.create_all(engine)
        inspector = inspect(engine)

        product_columns = {col["name"] for col in inspector.get_columns("loan_products")}
        workflow_columns = {col["name"] for col in inspector.get_columns("product_workflows")}
        workflow_version_columns = {col["name"] for col in inspector.get_columns("workflow_versions")}
        variable_columns = {col["name"] for col in inspector.get_columns("product_variables")}
        credit_request_columns = {col["name"] for col in inspector.get_columns("credit_requests")}
        evaluation_columns = {col["name"] for col in inspector.get_columns("loan_evaluations")}
        trace_columns = {col["name"] for col in inspector.get_columns("decision_traces")}

        self.assertIn("status", product_columns)
        self.assertIn("workflow_code", workflow_columns)
        self.assertIn("version_number", workflow_version_columns)
        self.assertIn("allowed_sources", variable_columns)
        self.assertIn("loan_product_code", credit_request_columns)
        self.assertIn("evaluation_id", credit_request_columns)
        self.assertIn("requested_amount", credit_request_columns)
        self.assertIn("workflow_code", evaluation_columns)
        self.assertIn("workflow_version_id", evaluation_columns)
        self.assertIn("pipeline_version", evaluation_columns)
        self.assertIn("trace_payload", trace_columns)


if __name__ == "__main__":
    unittest.main()
