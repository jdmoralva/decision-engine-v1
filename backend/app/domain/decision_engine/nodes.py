from collections.abc import Iterable
from typing import Any

from pydantic import BaseModel, Field

from backend.app.domain.decision_engine.contracts import (
    AppliedVersions,
    EngineDecisionEvidence,
    EngineDecisionTrace,
    EngineDecisionTraceNode,
    EngineEvaluationRequest,
)


class NodeExecutionResult(BaseModel):
    outcome: str
    next_node_key: str | None = None
    eligible: bool | None = None
    alerts_added: list[str] = Field(default_factory=list)
    blocks_added: list[str] = Field(default_factory=list)
    rules_applied: list[str] = Field(default_factory=list)
    consumed_variables: list[str] = Field(default_factory=list)
    produced_variables: list[str] = Field(default_factory=list)
    produced_effects: list[str] = Field(default_factory=list)
    evidence: list[EngineDecisionEvidence] = Field(default_factory=list)


class EngineExecutionContext:
    def __init__(self, request: EngineEvaluationRequest, applied_versions: AppliedVersions) -> None:
        self.request = request
        self.applied_versions = applied_versions
        self.product_result: dict[str, Any] = {}
        self.alerts: list[str] = []
        self.blocks: list[str] = []
        self.trace = EngineDecisionTrace(
            product_code=request.product_code,
            workflow_code=request.workflow_code,
            applied_versions=applied_versions,
        )
        self._eligible: bool = True

    @property
    def eligible(self) -> bool:
        return self._eligible and not self.blocks

    def mark_node_execution(
        self,
        *,
        node_key: str,
        node_type: str,
        result: NodeExecutionResult,
        branch_selected: str | None,
    ) -> None:
        self.alerts.extend(result.alerts_added)
        self.blocks.extend(result.blocks_added)
        self.trace.alerts = list(self.alerts)
        self.trace.blocks = list(self.blocks)
        self.trace.rules_applied.extend(result.rules_applied)
        self.trace.consumed_variables.extend(result.consumed_variables)
        self.trace.produced_variables.extend(result.produced_variables)
        self.trace.produced_effects.extend(result.produced_effects)
        self.trace.evidence.extend(result.evidence)
        if result.eligible is not None:
            self._eligible = result.eligible
        self.trace.nodes_executed.append(
            EngineDecisionTraceNode(
                node_key=node_key,
                node_type=node_type,
                outcome=result.outcome,
                branch_selected=branch_selected,
                alerts_added=list(result.alerts_added),
                blocks_added=list(result.blocks_added),
                rules_applied=list(result.rules_applied),
                consumed_variables=list(result.consumed_variables),
                produced_variables=list(result.produced_variables),
                produced_effects=list(result.produced_effects),
                evidence_keys=[
                    f"{item.source_type}:{item.source_key}:{item.field_name}"
                    for item in result.evidence
                ],
            )
        )

    def set_final_outcome(self, outcome: str) -> None:
        self.trace.final_outcome = outcome


class DecisionNode:
    node_key: str
    node_type: str

    async def run(self, context: EngineExecutionContext) -> NodeExecutionResult:
        raise NotImplementedError


def map_nodes_by_key(nodes: Iterable[DecisionNode]) -> dict[str, DecisionNode]:
    return {node.node_key: node for node in nodes}
