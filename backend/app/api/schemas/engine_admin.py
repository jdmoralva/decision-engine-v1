from typing import Any

from pydantic import BaseModel, Field


class AdminAuditQuery(BaseModel):
    evaluation_id: str | None = None
    request_id: str | None = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=50, ge=1, le=200)


class QueueExportFilters(BaseModel):
    start_date: str | None = None
    end_date: str | None = None
    status: str | None = None
    product_code: str | None = None
    workflow_code: str | None = None


class ProductCreateRequest(BaseModel):
    productCode: str = Field(min_length=1)
    name: str = Field(min_length=1)
    description: str | None = None


class ProductResponse(BaseModel):
    id: str
    productCode: str
    name: str
    description: str | None = None
    status: str


class WorkflowCreateRequest(BaseModel):
    workflowCode: str = Field(min_length=1)
    name: str = Field(min_length=1)
    description: str | None = None


class WorkflowResponse(BaseModel):
    id: str
    productCode: str
    workflowCode: str
    name: str
    description: str | None = None
    status: str


class ProductVariableCreateRequest(BaseModel):
    variableKey: str = Field(min_length=1)
    name: str = Field(min_length=1)
    businessMeaning: str = Field(min_length=1)
    description: str | None = None
    dataType: str = Field(min_length=1)
    required: bool = False
    allowedSource: str = Field(pattern="^(campaign_db|user_input|both)$")


class ProductVariableResponse(BaseModel):
    id: str
    productCode: str
    variableKey: str
    name: str
    businessMeaning: str
    description: str | None = None
    dataType: str
    required: bool
    allowedSource: str
    status: str


class VariableCatalogItemCreateRequest(BaseModel):
    productVariableId: str = Field(min_length=1)
    requiredInRuntime: bool = False
    defaultValue: Any | None = None
    sourcePolicyPayload: dict[str, Any] = Field(default_factory=dict)


class VariableCatalogCreateRequest(BaseModel):
    items: list[VariableCatalogItemCreateRequest] = Field(default_factory=list)


class VariableCatalogItemResponse(BaseModel):
    id: str
    productVariableId: str
    requiredInRuntime: bool
    defaultValue: str | None = None
    sourcePolicyPayload: dict[str, Any] = Field(default_factory=dict)


class VariableCatalogResponse(BaseModel):
    id: str
    productCode: str
    versionNumber: int
    status: str
    items: list[VariableCatalogItemResponse] = Field(default_factory=list)


class ParameterSetCreateRequest(BaseModel):
    workflowCode: str = Field(min_length=1)
    payload: dict[str, Any] = Field(default_factory=dict)


class ParameterSetResponse(BaseModel):
    id: str
    productCode: str
    workflowCode: str
    versionNumber: int
    status: str
    payload: dict[str, Any] = Field(default_factory=dict)


class PipelineNodeCreateRequest(BaseModel):
    nodeKey: str = Field(min_length=1)
    nodeType: str = Field(min_length=1)
    positionX: int | None = None
    positionY: int | None = None
    configPayload: dict[str, Any] = Field(default_factory=dict)


class PipelineStrategyCreateRequest(BaseModel):
    graphDefinition: dict[str, Any] = Field(default_factory=dict)
    nodes: list[PipelineNodeCreateRequest] = Field(default_factory=list)


class PipelineNodeResponse(BaseModel):
    id: str
    nodeKey: str
    nodeType: str
    positionX: int | None = None
    positionY: int | None = None
    configPayload: dict[str, Any] = Field(default_factory=dict)


class PipelineStrategyResponse(BaseModel):
    id: str
    productCode: str
    versionNumber: int
    status: str
    graphDefinition: dict[str, Any] = Field(default_factory=dict)
    nodes: list[PipelineNodeResponse] = Field(default_factory=list)


class RuleCreateRequest(BaseModel):
    name: str = Field(min_length=1)
    ruleType: str = Field(min_length=1)
    conditionExpression: str = Field(min_length=1)
    actionExpression: str = Field(min_length=1)
    parameters: dict[str, Any] = Field(default_factory=dict)


class RuleVersionResponse(BaseModel):
    id: str
    versionNumber: int
    ruleKey: str
    ruleName: str
    ruleType: str
    conditionExpression: str
    actionExpression: str
    parameters: dict[str, Any] = Field(default_factory=dict)
    status: str


class RuleResponse(BaseModel):
    id: str
    productCode: str
    workflowId: str
    name: str
    status: str
    activeVersion: RuleVersionResponse


class WorkflowVersionCreateRequest(BaseModel):
    variableCatalogVersionId: str = Field(min_length=1)
    parameterSetId: str = Field(min_length=1)
    pipelineStrategyId: str = Field(min_length=1)
    ruleVersionIds: list[str] = Field(default_factory=list)
    changeNotes: str | None = None


class WorkflowVersionResponse(BaseModel):
    id: str
    workflowId: str
    versionNumber: int
    status: str
    variableCatalogVersionId: str
    parameterSetId: str
    pipelineStrategyId: str
    ruleVersionIds: list[str] = Field(default_factory=list)
    changeNotes: str | None = None
