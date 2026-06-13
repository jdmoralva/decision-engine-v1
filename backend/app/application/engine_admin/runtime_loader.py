from __future__ import annotations

import json
from collections.abc import Callable

from sqlalchemy.orm import Session, sessionmaker

from backend.app.domain.decision_engine.contracts import AppliedVersions, EngineEvaluationRequest
from backend.app.domain.decision_engine.nodes import DecisionNode, NodeExecutionResult
from backend.app.domain.decision_engine.pipeline import PipelineNodeDefinition, PipelineStrategy
from backend.app.domain.decision_engine.registry import ProductEngineRuntime
from backend.app.infrastructure.db.session import get_session_factory
from backend.app.infrastructure.repositories.engine_admin import (
    RuntimeBundle,
    SqlAlchemyEngineAdminRepository,
)


def _identity_normalizer(request: EngineEvaluationRequest) -> EngineEvaluationRequest:
    return request


class PersistedDecisionNode(DecisionNode):
    def __init__(self, node_key: str, node_type: str, config_payload: str) -> None:
        self.node_key = node_key
        self.node_type = node_type
        self._config_payload = config_payload

    async def run(self, _context) -> NodeExecutionResult:
        try:
            payload = json.loads(self._config_payload) if self._config_payload else {}
        except json.JSONDecodeError:
            payload = {}
        outcome = str(payload.get("outcome", "done"))
        return NodeExecutionResult(outcome=outcome)


class RuntimeLoader:
    def __init__(self, session_factory: sessionmaker[Session] | None = None) -> None:
        self._session_factory = session_factory or get_session_factory()
        self._repository = SqlAlchemyEngineAdminRepository(self._session_factory)

    def list_active_workflows(self) -> list[tuple[str, str]]:
        return self._repository.list_active_workflows()

    def load_runtime(self, product_code: str, workflow_code: str) -> ProductEngineRuntime:
        bundle = self._repository.load_active_runtime_bundle(product_code, workflow_code)
        if bundle is None:
            raise ValueError(f"Active runtime not found for {product_code}/{workflow_code}")
        return self._build_runtime(bundle)

    def _build_runtime(self, bundle: RuntimeBundle) -> ProductEngineRuntime:
        graph_definition = json.loads(bundle.pipeline_strategy.graph_definition or "{}")
        start_node_key = str(graph_definition.get("start_node_key", bundle.pipeline_nodes[0].node_key))
        next_node_map = graph_definition.get("next_node_map", {})
        strategy = PipelineStrategy(
            strategy_key=f"{bundle.product_code}:{bundle.workflow_code}:{bundle.pipeline_strategy.version_number}",
            product_code=bundle.product_code,
            start_node_key=start_node_key,
            applied_versions=AppliedVersions(
                rule_set_version=",".join(
                    f"{rule.rule_key}:{rule.version_number}" for rule in bundle.rule_versions
                ),
                parameter_version=str(bundle.parameter_set.version_number),
                pipeline_version=str(bundle.pipeline_strategy.version_number),
            ),
            nodes=[
                PipelineNodeDefinition(
                    node_key=node.node_key,
                    node_type=node.node_type,
                    next_node_map=next_node_map.get(node.node_key, {}),
                )
                for node in bundle.pipeline_nodes
            ],
        )
        nodes = [
            PersistedDecisionNode(
                node_key=node.node_key,
                node_type=node.node_type,
                config_payload=node.config_payload,
            )
            for node in bundle.pipeline_nodes
        ]
        return ProductEngineRuntime(
            product_code=bundle.product_code,
            workflow_code=bundle.workflow_code,
            strategy=strategy,
            normalizer=_identity_normalizer,
            nodes=nodes,
        )
