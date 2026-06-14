"""Domain decision engine core package."""

from backend.app.domain.decision_engine.contracts import (
    AppliedVersions,
    EngineActorRef,
    EngineDecisionEvidence,
    EngineDecisionTrace,
    EngineDecisionTraceNode,
    EngineDocumentRef,
    EngineEvaluationRequest,
    EngineEvaluationResult,
    EngineExternalInput,
)
from backend.app.domain.decision_engine.bootstrap import (
    build_default_decision_engine_registry,
    build_persistence_backed_decision_engine_registry,
)
from backend.app.domain.decision_engine.exceptions import (
    DecisionEngineError,
    DecisionTopologyError,
    EngineRegistryError,
    EngineValidationError,
    UnknownProductError,
    UnknownWorkflowError,
)
from backend.app.domain.decision_engine.nodes import (
    DecisionNode,
    EngineExecutionContext,
    NodeExecutionResult,
)
from backend.app.domain.decision_engine.normalization import normalize_evaluation_request
from backend.app.domain.decision_engine.pipeline import (
    DecisionEngineOrchestrator,
    PipelineNodeDefinition,
    PipelineStrategy,
)
from backend.app.domain.decision_engine.runtime_definitions import (
    ProductDefinition,
    ProductRuntime,
    RuleDefinition,
    VariableDefinition,
    WorkflowDefinition,
    compile_product_runtime,
)
from backend.app.domain.decision_engine.registry import (
    DecisionEngineRegistry,
    ProductEngineRuntime,
)

__all__ = [
    "AppliedVersions",
    "build_default_decision_engine_registry",
    "build_persistence_backed_decision_engine_registry",
    "DecisionEngineError",
    "DecisionEngineOrchestrator",
    "DecisionEngineRegistry",
    "DecisionNode",
    "DecisionTopologyError",
    "EngineActorRef",
    "EngineDecisionEvidence",
    "EngineDecisionTrace",
    "EngineDecisionTraceNode",
    "EngineDocumentRef",
    "EngineEvaluationRequest",
    "EngineEvaluationResult",
    "EngineExecutionContext",
    "EngineExternalInput",
    "EngineRegistryError",
    "EngineValidationError",
    "NodeExecutionResult",
    "PipelineNodeDefinition",
    "PipelineStrategy",
    "ProductDefinition",
    "ProductEngineRuntime",
    "ProductRuntime",
    "RuleDefinition",
    "UnknownProductError",
    "UnknownWorkflowError",
    "VariableDefinition",
    "WorkflowDefinition",
    "compile_product_runtime",
    "normalize_evaluation_request",
]
