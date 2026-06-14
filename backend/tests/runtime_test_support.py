import importlib
import os
import tempfile
from pathlib import Path

from httpx import ASGITransport, AsyncClient


class RuntimeApiTestCaseMixin:
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "runtime_test.db"

        os.environ["APP_ENV"] = "test"
        os.environ["DATABASE_URL"] = f"sqlite+pysqlite:///{self.db_path.as_posix()}"
        os.environ["AUTH_SECRET_KEY"] = "test-secret-key"
        os.environ["ATTACHMENTS_STORAGE_DIR"] = str(Path(self.temp_dir.name) / "attachments")
        os.environ.pop("AI_ENABLED", None)
        os.environ.pop("OPENAI_API_KEY", None)
        os.environ.pop("GEMINI_API_KEY", None)

        from backend.app.config.settings import clear_settings_cache
        from backend.app.infrastructure.db.session import clear_database_caches

        clear_settings_cache()
        clear_database_caches()

        from backend.app.infrastructure.db.base import Base
        from backend.app.infrastructure.db.seed import seed_identity_data
        from backend.app.infrastructure.db.session import get_engine, get_session_factory

        engine = get_engine()
        Base.metadata.create_all(bind=engine)

        self._session_factory = get_session_factory()
        with self._session_factory() as session:
            seed_identity_data(session)

    def tearDown(self):
        from backend.app.config.settings import clear_settings_cache
        from backend.app.infrastructure.db.session import clear_database_caches

        clear_settings_cache()
        clear_database_caches()
        self.temp_dir.cleanup()

    def get_app(self):
        import backend.app.main as main_module

        return importlib.reload(main_module).app

    def build_transport(self) -> ASGITransport:
        return ASGITransport(app=self.get_app())

    async def login(self, client: AsyncClient, username: str) -> str:
        response = await client.post(
            "/api/v1/auth/login",
            json={"username": username, "password": f"{username}123"},
        )
        assert response.status_code == 200, response.text
        return response.json()["access_token"]

    async def auth_headers(self, client: AsyncClient, username: str) -> dict[str, str]:
        token = await self.login(client, username)
        return {"Authorization": f"Bearer {token}"}

    def activate_pld_runtime(self) -> dict[str, str]:
        from backend.app.infrastructure.db.seed import PLD_RUNTIME_IDS, seed_pld_runtime_bundle

        with self._session_factory() as session:
            seed_pld_runtime_bundle(session)

        return {
            "workflow_id": PLD_RUNTIME_IDS["workflow"],
            "workflow_version_id": PLD_RUNTIME_IDS["workflow_version"],
            "variable_catalog_version_id": PLD_RUNTIME_IDS["catalog"],
            "parameter_set_id": PLD_RUNTIME_IDS["parameter_set"],
            "pipeline_strategy_id": PLD_RUNTIME_IDS["pipeline"],
        }
