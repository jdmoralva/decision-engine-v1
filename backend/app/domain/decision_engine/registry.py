from collections.abc import Callable
from dataclasses import dataclass

from backend.app.domain.decision_engine.contracts import EngineEvaluationRequest
from backend.app.domain.decision_engine.nodes import DecisionNode
from backend.app.domain.decision_engine.pipeline import PipelineStrategy


@dataclass(frozen=True)
class ProductEngineRuntime:
    product_code: str
    workflow_code: str
    strategy: PipelineStrategy
    normalizer: Callable[[EngineEvaluationRequest], EngineEvaluationRequest]
    nodes: list[DecisionNode]


class DecisionEngineRegistry:
    def __init__(self) -> None:
        self._runtimes: dict[str, dict[str, ProductEngineRuntime]] = {}

    def register_product(
        self,
        *,
        product_code: str,
        workflow_code: str,
        strategy: PipelineStrategy,
        normalizer: Callable[[EngineEvaluationRequest], EngineEvaluationRequest],
        nodes: list[DecisionNode],
    ) -> None:
        product_key = product_code.strip().upper()
        workflow_key = workflow_code.strip()
        product_runtimes = self._runtimes.setdefault(product_key, {})
        product_runtimes[workflow_key] = ProductEngineRuntime(
            product_code=product_key,
            workflow_code=workflow_key,
            strategy=strategy,
            normalizer=normalizer,
            nodes=nodes,
        )

    def resolve(self, product_code: str, workflow_code: str) -> ProductEngineRuntime:
        from backend.app.domain.decision_engine.exceptions import (
            UnknownProductError,
            UnknownWorkflowError,
        )

        product_key = product_code.strip().upper()
        workflow_key = workflow_code.strip()
        product_runtimes = self._runtimes.get(product_key)
        if product_runtimes is None:
            raise UnknownProductError(
                f"Product '{product_key}' is not registered in the decision engine"
            )
        runtime = product_runtimes.get(workflow_key)
        if runtime is None:
            raise UnknownWorkflowError(
                f"Workflow '{workflow_key}' is not registered for product '{product_key}'"
            )
        return runtime
