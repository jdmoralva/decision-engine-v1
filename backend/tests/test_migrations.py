import sys
import tempfile
import unittest
from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


class MigrationTests(unittest.TestCase):
    def test_alembic_upgrade_creates_core_tables(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "migration_test.db"

            alembic_cfg = Config(str(ROOT / "backend" / "alembic.ini"))
            alembic_cfg.set_main_option(
                "script_location", str(ROOT / "backend" / "alembic")
            )
            alembic_cfg.set_main_option(
                "sqlalchemy.url", f"sqlite+pysqlite:///{db_path.as_posix()}"
            )

            command.upgrade(alembic_cfg, "head")

            engine = create_engine(f"sqlite+pysqlite:///{db_path.as_posix()}")
            try:
                inspector = inspect(engine)

                self.assertIn("credit_requests", inspector.get_table_names())
                self.assertIn("permissions", inspector.get_table_names())
                self.assertIn("role_permissions", inspector.get_table_names())
                self.assertIn("product_workflows", inspector.get_table_names())
                self.assertIn("workflow_versions", inspector.get_table_names())
                self.assertIn("product_variables", inspector.get_table_names())
                self.assertIn("variable_catalog_versions", inspector.get_table_names())
                self.assertIn("parameter_sets", inspector.get_table_names())
                self.assertIn("administrative_audit_events", inspector.get_table_names())
                self.assertIn("loan_evaluations", inspector.get_table_names())
                self.assertIn("decision_traces", inspector.get_table_names())

                product_columns = {column["name"] for column in inspector.get_columns("loan_products")}
                workflow_columns = {column["name"] for column in inspector.get_columns("product_workflows")}
                rule_set_columns = {column["name"] for column in inspector.get_columns("rule_sets")}

                self.assertTrue({"deleted_by", "deleted_at", "delete_reason"}.issubset(product_columns))
                self.assertTrue({"deleted_by", "deleted_at", "delete_reason"}.issubset(workflow_columns))
                self.assertTrue({"deleted_by", "deleted_at", "delete_reason"}.issubset(rule_set_columns))
            finally:
                engine.dispose()


if __name__ == "__main__":
    unittest.main()
