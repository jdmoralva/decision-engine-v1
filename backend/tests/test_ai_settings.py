import os
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


class AISettingsTests(unittest.TestCase):
    def tearDown(self):
        for key in (
            "DECISION_ENGINE_ENV_FILE",
            "AI_ENABLED",
            "AI_PROVIDER",
            "AI_TIMEOUT_SECONDS",
            "AI_MAX_RETRIES",
            "OPENAI_API_KEY",
            "OPENAI_MODEL_NAME",
            "GEMINI_API_KEY",
            "GEMINI_MODEL_NAME",
        ):
            os.environ.pop(key, None)

        from backend.app.config.settings import clear_settings_cache

        clear_settings_cache()

    def test_get_settings_loads_ai_configuration_from_env_file(self):
        env_contents = "\n".join(
            [
                "AI_ENABLED=true",
                "AI_PROVIDER=gemini",
                "AI_TIMEOUT_SECONDS=12.5",
                "AI_MAX_RETRIES=3",
                "OPENAI_API_KEY=test-openai-key",
                "OPENAI_MODEL_NAME=gpt-test",
                "GEMINI_API_KEY=test-gemini-key",
                "GEMINI_MODEL_NAME=gemini-test",
            ]
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            env_file = Path(tmpdir) / ".env"
            env_file.write_text(env_contents, encoding="utf-8")
            os.environ["DECISION_ENGINE_ENV_FILE"] = str(env_file)

            from backend.app.config.settings import clear_settings_cache, get_settings

            clear_settings_cache()
            settings = get_settings()

        self.assertTrue(settings.ai_enabled)
        self.assertEqual(settings.ai_provider, "gemini")
        self.assertEqual(settings.ai_timeout_seconds, 12.5)
        self.assertEqual(settings.ai_max_retries, 3)
        self.assertEqual(settings.openai_api_key, "test-openai-key")
        self.assertEqual(settings.openai_model_name, "gpt-test")
        self.assertEqual(settings.gemini_api_key, "test-gemini-key")
        self.assertEqual(settings.gemini_model_name, "gemini-test")

    def test_environment_variables_override_env_file_values(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            env_file = Path(tmpdir) / ".env"
            env_file.write_text(
                "AI_PROVIDER=gemini\nGEMINI_API_KEY=env-file-key\n",
                encoding="utf-8",
            )
            os.environ["DECISION_ENGINE_ENV_FILE"] = str(env_file)
            os.environ["AI_PROVIDER"] = "openai"
            os.environ["OPENAI_API_KEY"] = "runtime-openai-key"

            from backend.app.config.settings import clear_settings_cache, get_settings

            clear_settings_cache()
            settings = get_settings()

        self.assertEqual(settings.ai_provider, "openai")
        self.assertEqual(settings.openai_api_key, "runtime-openai-key")
