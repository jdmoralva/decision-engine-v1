import os
import sys
import tempfile
import unittest
from pathlib import Path

from sqlalchemy import select


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


class SeedTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "seed_test.db"

        os.environ["DATABASE_URL"] = f"sqlite+pysqlite:///{self.db_path.as_posix()}"

        from backend.app.config.settings import clear_settings_cache
        from backend.app.infrastructure.db.session import clear_database_caches, get_engine, get_session_factory
        from backend.app.infrastructure.db.base import Base
        from backend.app.infrastructure.db import models  # noqa: F401

        clear_settings_cache()
        clear_database_caches()

        engine = get_engine()
        Base.metadata.create_all(bind=engine)
        self.session_factory = get_session_factory()

    def tearDown(self):
        from backend.app.config.settings import clear_settings_cache
        from backend.app.infrastructure.db.session import clear_database_caches

        clear_settings_cache()
        clear_database_caches()
        self.temp_dir.cleanup()

    def test_seed_identity_data_is_idempotent_and_creates_default_users(self):
        from backend.app.infrastructure.db.models import Role, User
        from backend.app.infrastructure.db.seed import seed_identity_data

        with self.session_factory() as session:
            first_run = seed_identity_data(session)
            second_run = seed_identity_data(session)

            role_codes = set(session.execute(select(Role.code)).scalars().all())
            usernames = set(session.execute(select(User.username)).scalars().all())

        self.assertEqual(first_run["roles_created"], 7)
        self.assertEqual(first_run["users_created"], 7)
        self.assertEqual(second_run["roles_created"], 0)
        self.assertEqual(second_run["users_created"], 0)
        self.assertEqual(
            role_codes,
            {"admin", "analista", "evaluador", "auditor", "admin_negocio", "admin_riesgos", "plataforma"},
        )
        self.assertEqual(
            usernames,
            {"admin", "analista", "evaluador", "auditor", "negocio", "riesgos", "plataforma"},
        )


if __name__ == "__main__":
    unittest.main()
