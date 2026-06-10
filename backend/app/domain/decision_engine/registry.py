from collections.abc import Callable
from dataclasses import dataclass

from backend.app.domain.decision_engine.contracts import EngineEvaluationRequest
from backend.app.domain.decision_engine.exceptions import EngineRegistryError
from backend.app.domain.decision_engine.nodes import DecisionNode
from backend.app.domain.decision_engine.pipeline import PipelineStrategy


@dataclass(frozen=True)
class ProductEngineRuntime:
    product_code: str
    strategy: PipelineStrategy
    normalizer: Callable[[EngineEvaluationRequest], EngineEvaluationRequest]
    nodes: list[DecisionNode]


class DecisionEngineRegistry:
    def __init__(self) -> None:
        self._runtimes: dict[str, ProductEngineRuntime] = {}

    def register_product(
        self,
        *,
        product_code: str,
        strategy: PipelineStrategy,
        normalizer: Callable[[EngineEvaluationRequest], EngineEvaluationRequest],
        nodes: list[DecisionNode],
    ) -> None:
        key = product_code.strip().upper()
        self._runtimes[key] = ProductEngineRuntime(
            product_code=key,
            strategy=strategy,
            normalizer=normalizer,
            nodes=nodes,
        )

    def resolve(self, product_code: str) -> ProductEngineRuntime:
        key = product_code.strip().upper()
        runtime = self._runtimes.get(key)
        if runtime is None:
            raise EngineRegistryError(f"Product '{key}' is not registered in the decision engine")
        return runtime
