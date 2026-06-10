import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


class AIClientFactoryTests(unittest.TestCase):
    def test_factory_builds_openai_client_for_active_provider(self):
        from backend.app.application.ai.factory import build_ai_model_client
        from backend.app.application.ai.providers.openai_client import OpenAIModelClient
        from backend.app.config.settings import Settings

        settings = Settings(
            ai_enabled=True,
            ai_provider="openai",
            openai_api_key="test-openai-key",
            openai_model_name="gpt-test",
        )

        client = build_ai_model_client(settings)

        self.assertIsInstance(client, OpenAIModelClient)

    def test_factory_builds_gemini_client_for_active_provider(self):
        from backend.app.application.ai.factory import build_ai_model_client
        from backend.app.application.ai.providers.gemini_client import GeminiModelClient
        from backend.app.config.settings import Settings

        settings = Settings(
            ai_enabled=True,
            ai_provider="gemini",
            gemini_api_key="test-gemini-key",
            gemini_model_name="gemini-test",
        )

        client = build_ai_model_client(settings)

        self.assertIsInstance(client, GeminiModelClient)

    def test_factory_rejects_missing_api_key_for_active_provider(self):
        from backend.app.application.ai.exceptions import AIConfigurationError
        from backend.app.application.ai.factory import build_ai_model_client
        from backend.app.config.settings import Settings

        settings = Settings(ai_enabled=True, ai_provider="openai")

        with self.assertRaises(AIConfigurationError):
            build_ai_model_client(settings)

    def test_factory_rejects_disabled_ai(self):
        from backend.app.application.ai.exceptions import AIConfigurationError
        from backend.app.application.ai.factory import build_ai_model_client
        from backend.app.config.settings import Settings

        settings = Settings(ai_enabled=False, ai_provider="openai")

        with self.assertRaises(AIConfigurationError):
            build_ai_model_client(settings)
