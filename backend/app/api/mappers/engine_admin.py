import json

from backend.app.api.schemas.engine_admin import (
    ApprovalMetadataResponse,
    LifecycleEventMetadataResponse,
    ParameterSetResponse,
    PermissionResponse,
    PipelineNodeResponse,
    PipelineStrategyResponse,
    ProfilePermissionResponse,
    ProductDetailResponse,
    ProductListResponse,
    ProductResponse,
    ProductVariableResponse,
    RuleResponse,
    RuleVersionResponse,
    VariableCatalogItemResponse,
    VariableCatalogResponse,
    WorkflowDetailResponse,
    WorkflowListResponse,
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


def _approval(status: str, approved_by: str | None, approved_at) -> ApprovalMetadataResponse:
    if status == "draft":
        return ApprovalMetadataResponse(status="pending", approvedBy=None, approvedAt=None)
    return ApprovalMetadataResponse(status="approved", approvedBy=approved_by, approvedAt=approved_at)


def _last_modified(*timestamps):
    values = [value for value in timestamps if value is not None]
    return max(values)


def _lifecycle_event(performed_by: str | None, performed_at, reason: str | None = None) -> LifecycleEventMetadataResponse:
    return LifecycleEventMetadataResponse(
        performedBy=performed_by,
        performedAt=performed_at,
        reason=reason,
    )


def to_product_response(product) -> ProductResponse:
    return ProductResponse(
        id=product.code,
        productCode=product.code,
        name=product.name,
        description=product.description,
        status=product.status,
    )


def to_product_list_response(products: list) -> ProductListResponse:
    return ProductListResponse(items=[to_product_response(product) for product in products])


def to_product_detail_response(product, active_workflows: list[ProductWorkflow]) -> ProductDetailResponse:
    return ProductDetailResponse(
        id=product.code,
        productCode=product.code,
        name=product.name,
        description=product.description,
        status=product.status,
        createdBy=product.created_by,
        createdAt=product.created_at,
        lastModifiedAt=_last_modified(
            product.created_at,
            product.activated_at,
            product.retired_at,
            product.deleted_at,
        ),
        approval=_approval(product.status, product.activated_by, product.activated_at),
        retirement=_lifecycle_event(product.retired_by, product.retired_at),
        deletion=_lifecycle_event(product.deleted_by, product.deleted_at, product.delete_reason),
        activeWorkflows=[to_workflow_response(workflow) for workflow in active_workflows],
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


def to_workflow_list_response(workflows: list[ProductWorkflow]) -> WorkflowListResponse:
    return WorkflowListResponse(items=[to_workflow_response(workflow) for workflow in workflows])


def to_workflow_detail_response(
    workflow: ProductWorkflow,
    workflow_versions: list[WorkflowVersion],
    rule_version_ids: list[str],
) -> WorkflowDetailResponse:
    return WorkflowDetailResponse(
        id=workflow.id,
        productCode=workflow.product_code,
        workflowCode=workflow.workflow_code,
        name=workflow.name,
        description=workflow.description,
        status=workflow.status,
        createdBy=workflow.created_by,
        createdAt=workflow.created_at,
        lastModifiedAt=_last_modified(
            workflow.created_at,
            workflow.activated_at,
            workflow.retired_at,
            workflow.deleted_at,
        ),
        approval=_approval(workflow.status, workflow.activated_by, workflow.activated_at),
        retirement=_lifecycle_event(workflow.retired_by, workflow.retired_at),
        deletion=_lifecycle_event(workflow.deleted_by, workflow.deleted_at, workflow.delete_reason),
        variableCatalogVersionIds=[version.variable_catalog_version_id for version in workflow_versions],
        parameterSetIds=[version.parameter_set_id for version in workflow_versions],
        pipelineStrategyIds=[version.pipeline_strategy_id for version in workflow_versions],
        ruleVersionIds=rule_version_ids,
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
