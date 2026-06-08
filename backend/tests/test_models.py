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
            "credit_requests",
            "credit_request_status_history",
            "loan_evaluations",
            "evaluation_input_snapshots",
            "decision_traces",
            "decision_events",
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

        credit_request_columns = {col["name"] for col in inspector.get_columns("credit_requests")}
        evaluation_columns = {col["name"] for col in inspector.get_columns("loan_evaluations")}
        trace_columns = {col["name"] for col in inspector.get_columns("decision_traces")}

        self.assertIn("loan_product_code", credit_request_columns)
        self.assertIn("requested_amount", credit_request_columns)
        self.assertIn("pipeline_version", evaluation_columns)
        self.assertIn("trace_payload", trace_columns)


if __name__ == "__main__":
    unittest.main()
