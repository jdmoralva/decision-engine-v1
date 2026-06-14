import json

from backend.app.api.schemas.engine_admin import (
    ParameterSetResponse,
    PermissionResponse,
    PipelineNodeResponse,
    PipelineStrategyResponse,
    ProfilePermissionResponse,
    ProductResponse,
    ProductVariableResponse,
    RuleResponse,
    RuleVersionResponse,
    VariableCatalogItemResponse,
    VariableCatalogResponse,
    WorkflowResponse,
    WorkflowVersionResponse,
)
from backend.app.infrastructure.db.models import (
    ParameterSet,
    PipelineNode,
    PipelineStrategy,
    ProductVariable,
    ProductWorkflow,
    RuleSet,
    RuleVersion,
    VariableCatalogItem,
    VariableCatalogVersion,
    WorkflowVersion,
)


def _loads(payload: str | None) -> dict:
    if not payload:
        return {}
    return json.loads(payload)


def to_product_response(product) -> ProductResponse:
    return ProductResponse(
        id=product.code,
        productCode=product.code,
        name=product.name,
        description=product.description,
        status=product.status,
    )


def to_workflow_response(workflow: ProductWorkflow) -> WorkflowResponse:
    return WorkflowResponse(
        id=workflow.id,
        productCode=workflow.product_code,
        workflowCode=workflow.workflow_code,
        name=workflow.name,
        description=workflow.description,
        status=workflow.status,
    )


def to_variable_response(variable: ProductVariable) -> ProductVariableResponse:
    return ProductVariableResponse(
        id=variable.id,
        productCode=variable.product_code,
        variableKey=variable.variable_key,
        name=variable.name,
        businessMeaning=variable.business_meaning,
        description=variable.description,
        dataType=variable.data_type,
        required=variable.is_required,
        allowedSource=variable.allowed_sources,
        status=variable.status,
    )


def to_variable_catalog_response(
    catalog: VariableCatalogVersion,
    items: list[VariableCatalogItem],
) -> VariableCatalogResponse:
    return VariableCatalogResponse(
        id=catalog.id,
        productCode=catalog.product_code,
        versionNumber=catalog.version_number,
        status=catalog.status,
        items=[
            VariableCatalogItemResponse(
                id=item.id,
                productVariableId=item.product_variable_id,
                requiredInRuntime=item.is_required_in_runtime,
                defaultValue=item.default_value,
                sourcePolicyPayload=_loads(item.source_policy_payload),
            )
            for item in items
        ],
    )


def to_parameter_set_response(parameter_set: ParameterSet) -> ParameterSetResponse:
    return ParameterSetResponse(
        id=parameter_set.id,
        productCode=parameter_set.product_code,
        workflowCode=parameter_set.workflow_code,
        versionNumber=parameter_set.version_number,
        status=parameter_set.status,
        payload=_loads(parameter_set.payload),
    )


def to_pipeline_strategy_response(
    strategy: PipelineStrategy,
    nodes: list[PipelineNode],
) -> PipelineStrategyResponse:
    return PipelineStrategyResponse(
        id=strategy.id,
        productCode=strategy.loan_product_code,
        versionNumber=strategy.version_number,
        status=strategy.status,
        graphDefinition=_loads(strategy.graph_definition),
        nodes=[
            PipelineNodeResponse(
                id=node.id,
                nodeKey=node.node_key,
                nodeType=node.node_type,
                positionX=node.position_x,
                positionY=node.position_y,
                configPayload=_loads(node.config_payload),
            )
            for node in nodes
        ],
    )


def to_rule_version_response(rule_version: RuleVersion) -> RuleVersionResponse:
    return RuleVersionResponse(
        id=rule_version.id,
        versionNumber=rule_version.version_number,
        ruleKey=rule_version.rule_key,
        ruleName=rule_version.rule_name,
        ruleType=rule_version.rule_type,
        conditionExpression=rule_version.condition_expression,
        actionExpression=rule_version.action_expression,
        parameters=_loads(rule_version.parameters),
        status=rule_version.status,
    )


def to_rule_response(rule_set: RuleSet, workflow_id: str, rule_version: RuleVersion) -> RuleResponse:
    return RuleResponse(
        id=rule_set.id,
        productCode=rule_set.loan_product_code,
        workflowId=workflow_id,
        name=rule_set.name,
        status=rule_set.status,
        activeVersion=to_rule_version_response(rule_version),
    )


def to_workflow_version_response(
    workflow_version: WorkflowVersion,
    rule_version_ids: list[str],
) -> WorkflowVersionResponse:
    return WorkflowVersionResponse(
        id=workflow_version.id,
        workflowId=workflow_version.workflow_id,
        versionNumber=workflow_version.version_number,
        status=workflow_version.status,
        variableCatalogVersionId=workflow_version.variable_catalog_version_id,
        parameterSetId=workflow_version.parameter_set_id,
        pipelineStrategyId=workflow_version.pipeline_strategy_id,
        ruleVersionIds=rule_version_ids,
        changeNotes=workflow_version.change_notes,
    )


def to_profile_permission_response(
    role_code: str,
    permissions: list[dict[str, str | None]],
) -> ProfilePermissionResponse:
    return ProfilePermissionResponse(
        roleCode=role_code,
        permissions=[
            PermissionResponse(
                code=str(permission["code"]),
                name=str(permission["name"]),
                description=(
                    None if permission.get("description") is None else str(permission["description"])
                ),
            )
            for permission in permissions
        ],
    )
