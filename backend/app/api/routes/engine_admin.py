from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse

from backend.app.api.mappers.engine_admin import (
    to_parameter_set_response,
    to_pipeline_strategy_response,
    to_profile_permission_response,
    to_product_response,
    to_rule_response,
    to_variable_catalog_response,
    to_variable_response,
    to_workflow_response,
    to_workflow_version_response,
)
from backend.app.api.schemas.contracts import ContractError, StructuredErrorResponse
from backend.app.api.schemas.engine_admin import (
    ParameterSetCreateRequest,
    ParameterSetResponse,
    PipelineStrategyCreateRequest,
    PipelineStrategyResponse,
    ProfilePermissionAssignmentRequest,
    ProfilePermissionResponse,
    ProductCreateRequest,
    ProductResponse,
    ProductVariableCreateRequest,
    ProductVariableResponse,
    RuleCreateRequest,
    RuleResponse,
    VariableCatalogCreateRequest,
    VariableCatalogResponse,
    WorkflowCreateRequest,
    WorkflowResponse,
    WorkflowVersionCreateRequest,
    WorkflowVersionResponse,
)
from backend.app.application.engine_admin.activation_rules import EngineAdminValidationError
from backend.app.application.engine_admin.service import EngineAdminService
from backend.app.infrastructure.repositories.audit_events import AuditEventWriter
from backend.app.infrastructure.db.session import get_session_factory
from backend.app.security.dependencies import get_current_user_context, require_permission


router = APIRouter(prefix="/admin/engine", tags=["engine-admin"])

error_responses = {
    400: {"model": StructuredErrorResponse, "description": "Business validation error."},
    401: {"model": StructuredErrorResponse, "description": "Authentication required."},
    403: {"model": StructuredErrorResponse, "description": "Forbidden."},
    404: {"model": StructuredErrorResponse, "description": "Resource not found."},
    409: {"model": StructuredErrorResponse, "description": "Conflicting request state."},
    422: {"description": "Request validation error."},
}


def _service() -> EngineAdminService:
    session_factory = get_session_factory()
    return EngineAdminService(session_factory, AuditEventWriter(session_factory))


def _validation_error_response(message: str, status_code: int = status.HTTP_409_CONFLICT) -> JSONResponse:
    payload = StructuredErrorResponse(
        error=ContractError(code="ENGINE_ADMIN_VALIDATION", message=message)
    )
    return JSONResponse(status_code=status_code, content=payload.model_dump())


@router.post("/products", response_model=ProductResponse, status_code=status.HTTP_201_CREATED, responses=error_responses)
def create_product(
    payload: ProductCreateRequest,
    context: tuple = Depends(require_permission("administrar_productos")),
) -> ProductResponse | JSONResponse:
    user, _roles = context
    try:
        return to_product_response(_service().create_product(payload, user.id))
    except EngineAdminValidationError as exc:
        return _validation_error_response(str(exc))


@router.post("/products/{productCode}/activation", response_model=ProductResponse, responses=error_responses)
def activate_product(
    productCode: str,
    context: tuple = Depends(require_permission("aprobar_activacion_motor")),
) -> ProductResponse | JSONResponse:
    user, _roles = context
    try:
        return to_product_response(_service().activate_product(productCode, user.id))
    except EngineAdminValidationError as exc:
        return _validation_error_response(str(exc))


@router.post("/products/{productCode}/retirement", response_model=ProductResponse, responses=error_responses)
def retire_product(
    productCode: str,
    context: tuple = Depends(require_permission("aprobar_activacion_motor")),
) -> ProductResponse | JSONResponse:
    user, _roles = context
    try:
        return to_product_response(_service().retire_product(productCode, user.id))
    except EngineAdminValidationError as exc:
        return _validation_error_response(str(exc))


@router.delete("/products/{productCode}", status_code=status.HTTP_204_NO_CONTENT, responses=error_responses)
def delete_product(
    productCode: str,
    context: tuple = Depends(get_current_user_context),
) -> JSONResponse:
    user, roles = context
    try:
        _service().delete_product(productCode, user.id, roles)
    except EngineAdminValidationError as exc:
        return _validation_error_response(str(exc))
    return JSONResponse(status_code=status.HTTP_204_NO_CONTENT, content=None)


@router.post("/products/{productCode}/workflows", response_model=WorkflowResponse, status_code=status.HTTP_201_CREATED, responses=error_responses)
def create_workflow(
    productCode: str,
    payload: WorkflowCreateRequest,
    context: tuple = Depends(require_permission("administrar_workflows")),
) -> WorkflowResponse | JSONResponse:
    user, _roles = context
    try:
        return to_workflow_response(_service().create_workflow(productCode, payload, user.id))
    except EngineAdminValidationError as exc:
        return _validation_error_response(str(exc))


@router.delete("/workflows/{workflowId}", status_code=status.HTTP_204_NO_CONTENT, responses=error_responses)
def delete_workflow(
    workflowId: str,
    context: tuple = Depends(get_current_user_context),
) -> JSONResponse:
    user, roles = context
    try:
        _service().delete_workflow(workflowId, user.id, roles)
    except EngineAdminValidationError as exc:
        return _validation_error_response(str(exc))
    return JSONResponse(status_code=status.HTTP_204_NO_CONTENT, content=None)


@router.post("/products/{productCode}/variables", response_model=ProductVariableResponse, status_code=status.HTTP_201_CREATED, responses=error_responses)
def create_variable(
    productCode: str,
    payload: ProductVariableCreateRequest,
    context: tuple = Depends(require_permission("administrar_variables")),
) -> ProductVariableResponse | JSONResponse:
    user, _roles = context
    try:
        return to_variable_response(_service().create_variable(productCode, payload, user.id))
    except EngineAdminValidationError as exc:
        return _validation_error_response(str(exc))


@router.post("/variables/{variableId}/activation", response_model=ProductVariableResponse, responses=error_responses)
def activate_variable(
    variableId: str,
    context: tuple = Depends(require_permission("aprobar_activacion_motor")),
) -> ProductVariableResponse | JSONResponse:
    user, _roles = context
    try:
        return to_variable_response(_service().activate_variable(variableId, user.id))
    except EngineAdminValidationError as exc:
        return _validation_error_response(str(exc))


@router.post("/products/{productCode}/variable-catalogs", response_model=VariableCatalogResponse, status_code=status.HTTP_201_CREATED, responses=error_responses)
def create_variable_catalog(
    productCode: str,
    payload: VariableCatalogCreateRequest,
    context: tuple = Depends(require_permission("administrar_catalogos_variables")),
) -> VariableCatalogResponse | JSONResponse:
    user, _roles = context
    try:
        catalog, items = _service().create_variable_catalog(productCode, payload, user.id)
        return to_variable_catalog_response(catalog, items)
    except EngineAdminValidationError as exc:
        return _validation_error_response(str(exc))


@router.post("/variable-catalogs/{catalogVersionId}/activation", response_model=VariableCatalogResponse, responses=error_responses)
def activate_variable_catalog(
    catalogVersionId: str,
    context: tuple = Depends(require_permission("aprobar_activacion_motor")),
) -> VariableCatalogResponse | JSONResponse:
    user, _roles = context
    try:
        catalog, items = _service().activate_variable_catalog(catalogVersionId, user.id)
        return to_variable_catalog_response(catalog, items)
    except EngineAdminValidationError as exc:
        return _validation_error_response(str(exc))


@router.post("/products/{productCode}/parameter-sets", response_model=ParameterSetResponse, status_code=status.HTTP_201_CREATED, responses=error_responses)
def create_parameter_set(
    productCode: str,
    payload: ParameterSetCreateRequest,
    context: tuple = Depends(require_permission("administrar_parametros")),
) -> ParameterSetResponse | JSONResponse:
    user, _roles = context
    try:
        return to_parameter_set_response(_service().create_parameter_set(productCode, payload, user.id))
    except EngineAdminValidationError as exc:
        return _validation_error_response(str(exc))


@router.post("/parameter-sets/{parameterSetId}/activation", response_model=ParameterSetResponse, responses=error_responses)
def activate_parameter_set(
    parameterSetId: str,
    context: tuple = Depends(require_permission("aprobar_activacion_motor")),
) -> ParameterSetResponse | JSONResponse:
    user, _roles = context
    try:
        return to_parameter_set_response(_service().activate_parameter_set(parameterSetId, user.id))
    except EngineAdminValidationError as exc:
        return _validation_error_response(str(exc))


@router.post("/products/{productCode}/pipeline-strategies", response_model=PipelineStrategyResponse, status_code=status.HTTP_201_CREATED, responses=error_responses)
def create_pipeline_strategy(
    productCode: str,
    payload: PipelineStrategyCreateRequest,
    context: tuple = Depends(require_permission("administrar_pipeline")),
) -> PipelineStrategyResponse | JSONResponse:
    user, _roles = context
    try:
        strategy, nodes = _service().create_pipeline_strategy(productCode, payload, user.id)
        return to_pipeline_strategy_response(strategy, nodes)
    except EngineAdminValidationError as exc:
        return _validation_error_response(str(exc))


@router.post("/pipeline-strategies/{strategyId}/activation", response_model=PipelineStrategyResponse, responses=error_responses)
def activate_pipeline_strategy(
    strategyId: str,
    context: tuple = Depends(require_permission("aprobar_activacion_motor")),
) -> PipelineStrategyResponse | JSONResponse:
    user, _roles = context
    try:
        strategy, nodes = _service().activate_pipeline_strategy(strategyId, user.id)
        return to_pipeline_strategy_response(strategy, nodes)
    except EngineAdminValidationError as exc:
        return _validation_error_response(str(exc))


@router.post("/workflows/{workflowId}/rules", response_model=RuleResponse, status_code=status.HTTP_201_CREATED, responses=error_responses)
def create_rule(
    workflowId: str,
    payload: RuleCreateRequest,
    context: tuple = Depends(require_permission("administrar_reglas")),
) -> RuleResponse | JSONResponse:
    user, _roles = context
    try:
        rule_set, rule_version = _service().create_rule(workflowId, payload, user.id)
        return to_rule_response(rule_set, workflowId, rule_version)
    except EngineAdminValidationError as exc:
        return _validation_error_response(str(exc))


@router.delete("/rules/{ruleId}", status_code=status.HTTP_204_NO_CONTENT, responses=error_responses)
def delete_rule(
    ruleId: str,
    context: tuple = Depends(get_current_user_context),
) -> JSONResponse:
    user, roles = context
    try:
        _service().delete_rule(ruleId, user.id, roles)
    except EngineAdminValidationError as exc:
        return _validation_error_response(str(exc))
    return JSONResponse(status_code=status.HTTP_204_NO_CONTENT, content=None)


@router.get("/profiles/{roleCode}/permissions", response_model=ProfilePermissionResponse, responses=error_responses)
def get_profile_permissions(
    roleCode: str,
    _context: tuple = Depends(require_permission("administrar_perfiles_permisos")),
) -> ProfilePermissionResponse | JSONResponse:
    try:
        return to_profile_permission_response(roleCode, _service().get_profile_permissions(roleCode))
    except EngineAdminValidationError as exc:
        return _validation_error_response(str(exc), status.HTTP_404_NOT_FOUND)


@router.put("/profiles/{roleCode}/permissions", response_model=ProfilePermissionResponse, responses=error_responses)
def replace_profile_permissions(
    roleCode: str,
    payload: ProfilePermissionAssignmentRequest,
    context: tuple = Depends(require_permission("administrar_perfiles_permisos")),
) -> ProfilePermissionResponse | JSONResponse:
    user, _roles = context
    try:
        permissions = _service().replace_profile_permissions(roleCode, payload, user.id)
        return to_profile_permission_response(roleCode, permissions)
    except EngineAdminValidationError as exc:
        return _validation_error_response(str(exc), status.HTTP_404_NOT_FOUND)


@router.post("/rule-versions/{ruleVersionId}/activation", response_model=RuleResponse, responses=error_responses)
def activate_rule_version(
    ruleVersionId: str,
    context: tuple = Depends(require_permission("aprobar_activacion_motor")),
) -> RuleResponse | JSONResponse:
    user, _roles = context
    try:
        rule_set, rule_version = _service().activate_rule_version(ruleVersionId, user.id)
        workflow_id = "unknown"
        return to_rule_response(rule_set, workflow_id, rule_version)
    except EngineAdminValidationError as exc:
        return _validation_error_response(str(exc))


@router.post("/workflows/{workflowId}/versions", response_model=WorkflowVersionResponse, status_code=status.HTTP_201_CREATED, responses=error_responses)
def create_workflow_version(
    workflowId: str,
    payload: WorkflowVersionCreateRequest,
    context: tuple = Depends(require_permission("solicitar_versionado_motor")),
) -> WorkflowVersionResponse | JSONResponse:
    user, _roles = context
    try:
        result = _service().create_workflow_version(workflowId, payload, user.id)
        return to_workflow_version_response(result.workflow_version, result.rule_version_ids)
    except EngineAdminValidationError as exc:
        return _validation_error_response(str(exc))


@router.post("/workflow-versions/{versionId}/activation", response_model=WorkflowVersionResponse, responses=error_responses)
def activate_workflow_version(
    versionId: str,
    context: tuple = Depends(require_permission("aprobar_activacion_motor")),
) -> WorkflowVersionResponse | JSONResponse:
    user, _roles = context
    try:
        result = _service().activate_workflow_version(versionId, user.id)
        return to_workflow_version_response(result.workflow_version, result.rule_version_ids)
    except EngineAdminValidationError as exc:
        return _validation_error_response(str(exc))


@router.post("/workflow-versions/{versionId}/retirement", response_model=WorkflowVersionResponse, responses=error_responses)
def retire_workflow_version(
    versionId: str,
    context: tuple = Depends(require_permission("aprobar_activacion_motor")),
) -> WorkflowVersionResponse | JSONResponse:
    user, _roles = context
    try:
        result = _service().retire_workflow_version(versionId, user.id)
        return to_workflow_version_response(result.workflow_version, result.rule_version_ids)
    except EngineAdminValidationError as exc:
        return _validation_error_response(str(exc))
