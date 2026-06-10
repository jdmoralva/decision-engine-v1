from collections import deque

from pydantic import BaseModel, Field

from backend.app.domain.decision_engine.contracts import (
    AppliedVersions,
    EngineEvaluationRequest,
    EngineEvaluationResult,
)
from backend.app.domain.decision_engine.exceptions import DecisionTopologyError
from backend.app.domain.decision_engine.nodes import (
    EngineExecutionContext,
    NodeExecutionResult,
    map_nodes_by_key,
)


class PipelineNodeDefinition(BaseModel):
    node_key: str
    node_type: str
    next_node_map: dict[str, str] = Field(default_factory=dict)


class PipelineStrategy(BaseModel):
    strategy_key: str
    product_code: str
    start_node_key: str
    applied_versions: AppliedVersions = Field(default_factory=AppliedVersions)
    nodes: list[PipelineNodeDefinition] = Field(default_factory=list)


class DecisionEngineOrchestrator:
    def __init__(self, nodes: list) -> None:
        self._nodes_by_key = map_nodes_by_key(nodes)

    def validate_strategy(self, strategy: PipelineStrategy) -> None:
        definitions_by_key = {node.node_key: node for node in strategy.nodes}
        if strategy.start_node_key not in definitions_by_key:
            raise DecisionTopologyError("Pipeline start node is not defined")

        for definition in strategy.nodes:
            if definition.node_key not in self._nodes_by_key:
                raise DecisionTopologyError(
                    f"Pipeline node '{definition.node_key}' is not registered"
                )
            for target in definition.next_node_map.values():
                if target not in definitions_by_key:
                    raise DecisionTopologyError(
                        f"Pipeline node '{definition.node_key}' references unknown "
                        f"target '{target}'"
                    )

        visited: set[str] = set()
        recursion_stack: set[str] = set()

        def visit(node_key: str) -> None:
            if node_key in recursion_stack:
                raise DecisionTopologyError(
                    f"Pipeline node '{node_key}' participates in a cycle"
                )
            if node_key in visited:
                return

            recursion_stack.add(node_key)
            for target in definitions_by_key[node_key].next_node_map.values():
                visit(target)
            recursion_stack.remove(node_key)
            visited.add(node_key)

        visit(strategy.start_node_key)

        reachable = set()
        queue = deque([strategy.start_node_key])
        while queue:
            node_key = queue.popleft()
            if node_key in reachable:
                continue
            reachable.add(node_key)
            queue.extend(definitions_by_key[node_key].next_node_map.values())

        for definition in strategy.nodes:
            if definition.node_key not in reachable:
                raise DecisionTopologyError(
                    f"Pipeline node '{definition.node_key}' is unreachable from the start node"
                )

    async def evaluate(
        self, request: EngineEvaluationRequest, strategy: PipelineStrategy
    ) -> EngineEvaluationResult:
        self.validate_strategy(strategy)
        definitions_by_key = {node.node_key: node for node in strategy.nodes}
        context = EngineExecutionContext(
            request=request,
            applied_versions=strategy.applied_versions,
        )
        current_node_key = strategy.start_node_key
        last_result: NodeExecutionResult | None = None

        while current_node_key is not None:
            node = self._nodes_by_key[current_node_key]
            definition = definitions_by_key[current_node_key]
            result = await node.run(context)
            branch_selected = result.next_node_key
            if branch_selected is None:
                branch_selected = definition.next_node_map.get(result.outcome)
            context.mark_node_execution(
                node_key=node.node_key,
                node_type=node.node_type,
                result=result,
                branch_selected=branch_selected,
            )
            current_node_key = branch_selected
            last_result = result
        context.set_final_outcome(
            last_result.outcome if last_result is not None else "not_executed"
        )
        return EngineEvaluationResult(
            product_code=request.product_code,
            eligible=context.eligible,
            alerts=list(context.alerts),
            blocks=list(context.blocks),
            applied_versions=strategy.applied_versions,
            product_result=dict(context.product_result),
            decision_trace=context.trace,
        )
