class DecisionEngineError(Exception):
    """Base exception for the decision engine domain."""


class EngineValidationError(DecisionEngineError):
    """Raised when a shared engine contract is invalid after normalization."""


class DecisionTopologyError(DecisionEngineError):
    """Raised when a pipeline strategy has an invalid graph definition."""


class EngineRegistryError(DecisionEngineError):
    """Raised when a product runtime cannot be resolved."""


class UnknownProductError(EngineRegistryError):
    """Raised when a product is not registered in the decision engine."""


class UnknownWorkflowError(EngineRegistryError):
    """Raised when a workflow is not registered for a known product."""
