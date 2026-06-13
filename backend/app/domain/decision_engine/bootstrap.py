from sqlalchemy.orm import Session, sessionmaker

from backend.app.domain.decision_engine.pld import compile_pld_runtime
from backend.app.domain.decision_engine.registry import DecisionEngineRegistry
from backend.app.infrastructure.db.session import get_session_factory


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


def build_persistence_backed_decision_engine_registry(
    session_factory: sessionmaker[Session] | None = None,
    *,
    include_default_fallback: bool = True,
) -> DecisionEngineRegistry:
    from backend.app.application.engine_admin.runtime_loader import RuntimeLoader

    registry = DecisionEngineRegistry()
    loader = RuntimeLoader(session_factory or get_session_factory())

    for product_code, workflow_code in loader.list_active_workflows():
        runtime = loader.load_runtime(product_code, workflow_code)
        registry.register_product(
            product_code=runtime.product_code,
            workflow_code=runtime.workflow_code,
            strategy=runtime.strategy,
            normalizer=runtime.normalizer,
            nodes=runtime.nodes,
        )

    if include_default_fallback and not loader.list_active_workflows():
        return build_default_decision_engine_registry()

    return registry
