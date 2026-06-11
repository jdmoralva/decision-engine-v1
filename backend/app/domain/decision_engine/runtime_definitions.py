from collections.abc import Callable
from dataclasses import dataclass
from typing import Literal

from pydantic import BaseModel, Field

from backend.app.domain.decision_engine.contracts import EngineEvaluationRequest
from backend.app.domain.decision_engine.exceptions import EngineValidationError
from backend.app.domain.decision_engine.nodes import DecisionNode
from backend.app.domain.decision_engine.pipeline import PipelineStrategy


VariableKind = Literal["input", "derived", "metric", "flag", "decision"]
VariableDataType = Literal["string", "integer", "number", "boolean", "object"]
RuleType = Literal["eligibility", "derivation", "metric", "block", "alert", "decision"]


class VariableDefinition(BaseModel):
    variable_key: str = Field(min_length=1)
    variable_kind: VariableKind
    data_type: VariableDataType
    required: bool = False
    allowed_in_rules: bool = True
    persist_in_evidence: bool = False


class RuleDefinition(BaseModel):
    rule_code: str = Field(min_length=1)
    rule_type: RuleType
    product_code: str = Field(min_length=1)
    workflow_code: str = Field(min_length=1)
    consumes_variables: list[str] = Field(default_factory=list)
    produces_variable: str | None = None
    produces_effect: str | None = None
    priority: int = 100
    version: str = Field(min_length=1)


class WorkflowDefinition(BaseModel):
    workflow_code: str = Field(min_length=1)
    product_code: str = Field(min_length=1)
    name: str = Field(min_length=1)
    description: str | None = None
    pipeline_version: str = Field(min_length=1)
    rule_pack_version: str = Field(min_length=1)
    variables: list[VariableDefinition] = Field(default_factory=list)
    rules: list[RuleDefinition] = Field(default_factory=list)


class ProductDefinition(BaseModel):
    product_code: str = Field(min_length=1)
    name: str = Field(min_length=1)
    is_active: bool = True
    workflows: list[WorkflowDefinition] = Field(default_factory=list)


@dataclass(frozen=True)
class ProductRuntime:
    product_code: str
    workflow_code: str
    workflow: WorkflowDefinition
    strategy: PipelineStrategy
    normalizer: Callable[[EngineEvaluationRequest], EngineEvaluationRequest]
    nodes: list[DecisionNode]
    variable_catalog: dict[str, VariableDefinition]
    rules: list[RuleDefinition]


def compile_product_runtime(
    *,
    product_definition: ProductDefinition,
    workflow_code: str,
    strategy: PipelineStrategy,
    normalizer: Callable[[EngineEvaluationRequest], EngineEvaluationRequest],
    nodes: list[DecisionNode],
) -> ProductRuntime:
    product_code = product_definition.product_code.strip().upper()
    workflow_key = workflow_code.strip()

    if not product_definition.is_active:
        raise EngineValidationError(f"Product '{product_code}' is inactive")
    if strategy.product_code.strip().upper() != product_code:
        raise EngineValidationError(
            f"Pipeline strategy product '{strategy.product_code}' does not match '{product_code}'"
        )

    workflow = _resolve_workflow(product_definition, workflow_key)
    variable_catalog = _build_variable_catalog(workflow)
    _validate_rules(product_code=product_code, workflow=workflow, variable_catalog=variable_catalog)

    return ProductRuntime(
        product_code=product_code,
        workflow_code=workflow.workflow_code,
        workflow=workflow,
        strategy=strategy,
        normalizer=normalizer,
        nodes=nodes,
        variable_catalog=variable_catalog,
        rules=sorted(workflow.rules, key=lambda rule: (rule.priority, rule.rule_code)),
    )


def _resolve_workflow(
    product_definition: ProductDefinition, workflow_code: str
) -> WorkflowDefinition:
    for workflow in product_definition.workflows:
        if workflow.workflow_code == workflow_code:
            return workflow
    raise EngineValidationError(
        f"Workflow '{workflow_code}' is not defined for product '{product_definition.product_code}'"
    )


def _build_variable_catalog(workflow: WorkflowDefinition) -> dict[str, VariableDefinition]:
    catalog: dict[str, VariableDefinition] = {}
    for variable in workflow.variables:
        if variable.variable_key in catalog:
            raise EngineValidationError(
                f"Variable '{variable.variable_key}' is duplicated in workflow '{workflow.workflow_code}'"
            )
        catalog[variable.variable_key] = variable
    return catalog


def _validate_rules(
    *,
    product_code: str,
    workflow: WorkflowDefinition,
    variable_catalog: dict[str, VariableDefinition],
) -> None:
    for rule in workflow.rules:
        if rule.product_code.strip().upper() != product_code:
            raise EngineValidationError(
                f"Rule '{rule.rule_code}' belongs to product '{rule.product_code}' instead of '{product_code}'"
            )
        if rule.workflow_code != workflow.workflow_code:
            raise EngineValidationError(
                f"Rule '{rule.rule_code}' belongs to workflow '{rule.workflow_code}' instead of '{workflow.workflow_code}'"
            )
        for variable_key in rule.consumes_variables:
            variable = variable_catalog.get(variable_key)
            if variable is None:
                raise EngineValidationError(
                    f"Rule '{rule.rule_code}' consumes unknown variable '{variable_key}'"
                )
            if not variable.allowed_in_rules:
                raise EngineValidationError(
                    f"Variable '{variable_key}' is not allowed in rules for workflow '{workflow.workflow_code}'"
                )
        if rule.produces_variable is not None and rule.produces_variable not in variable_catalog:
            raise EngineValidationError(
                f"Rule '{rule.rule_code}' produces unknown variable '{rule.produces_variable}'"
            )
