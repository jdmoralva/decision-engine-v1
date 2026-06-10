from backend.app.application.ai.client import AIModelClient
from backend.app.application.ai.exceptions import AIConfigurationError
from backend.app.application.ai.providers.gemini_client import GeminiModelClient
from backend.app.application.ai.providers.openai_client import OpenAIModelClient
from backend.app.config.settings import Settings


def build_ai_model_client(settings: Settings) -> AIModelClient:
    if not settings.ai_enabled:
        raise AIConfigurationError("AI integration is disabled")

    if settings.ai_provider == "openai":
        if not settings.openai_api_key:
            raise AIConfigurationError("OPENAI_API_KEY is required for provider 'openai'")
        return OpenAIModelClient(
            api_key=settings.openai_api_key,
            model_name=settings.openai_model_name,
            timeout_seconds=settings.ai_timeout_seconds,
            max_retries=settings.ai_max_retries,
        )

    if settings.ai_provider == "gemini":
        if not settings.gemini_api_key:
            raise AIConfigurationError("GEMINI_API_KEY is required for provider 'gemini'")
        return GeminiModelClient(
            api_key=settings.gemini_api_key,
            model_name=settings.gemini_model_name,
            timeout_seconds=settings.ai_timeout_seconds,
            max_retries=settings.ai_max_retries,
        )

    raise AIConfigurationError(f"Unsupported AI provider '{settings.ai_provider}'")
