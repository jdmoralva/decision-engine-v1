import os
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


class SettingsTests(unittest.TestCase):
    def test_settings_use_environment_defaults(self):
        os.environ.pop("APP_ENV", None)
        os.environ.pop("APP_NAME", None)

        from backend.app.config.settings import Settings

        settings = Settings()

        self.assertEqual(settings.app_env, "development")
        self.assertEqual(settings.app_name, "decision-engine-api")
        self.assertEqual(settings.api_v1_prefix, "/api/v1")


if __name__ == "__main__":
    unittest.main()
