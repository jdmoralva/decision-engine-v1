class AIServiceError(Exception):
    """Base exception for AI service integration."""


class AIConfigurationError(AIServiceError):
    """Raised when AI configuration is missing or invalid."""


class AIProviderError(AIServiceError):
    """Raised when a provider returns a non-recoverable error."""


class AITemporaryError(AIServiceError):
    """Raised when a provider fails transiently after retries."""


class AITimeoutError(AITemporaryError):
    """Raised when the provider times out after retries."""
