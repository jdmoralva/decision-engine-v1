class DecisionEngineError(Exception):
    """Base exception for the decision engine domain."""


class EngineValidationError(DecisionEngineError):
    """Raised when a shared engine contract is invalid after normalization."""


class DecisionTopologyError(DecisionEngineError):
    """Raised when a pipeline strategy has an invalid graph definition."""


class EngineRegistryError(DecisionEngineError):
    """Raised when a product runtime cannot be resolved."""
