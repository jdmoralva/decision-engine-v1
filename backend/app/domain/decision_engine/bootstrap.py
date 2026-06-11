from backend.app.domain.decision_engine.pld import compile_pld_runtime
from backend.app.domain.decision_engine.registry import DecisionEngineRegistry


def build_default_decision_engine_registry() -> DecisionEngineRegistry:
    registry = DecisionEngineRegistry()
    pld_runtime = compile_pld_runtime(workflow_code="standard")
    registry.register_product(
        product_code=pld_runtime.product_code,
        workflow_code=pld_runtime.workflow_code,
        strategy=pld_runtime.strategy,
        normalizer=pld_runtime.normalizer,
        nodes=pld_runtime.nodes,
    )
    return registry
