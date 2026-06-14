from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.infrastructure.db.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    username: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    display_name: Mapped[str | None] = mapped_column(String(150))
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[str] = mapped_column(DateTime, nullable=False)


class Role(Base):
    __tablename__ = "roles"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[str] = mapped_column(DateTime, nullable=False)


class Permission(Base):
    __tablename__ = "permissions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    code: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[str] = mapped_column(DateTime, nullable=False)


class RolePermission(Base):
    __tablename__ = "role_permissions"
    __table_args__ = (UniqueConstraint("role_id", "permission_id", name="uq_role_permission"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    role_id: Mapped[str] = mapped_column(ForeignKey("roles.id"), nullable=False)
    permission_id: Mapped[str] = mapped_column(ForeignKey("permissions.id"), nullable=False)
    created_at: Mapped[str] = mapped_column(DateTime, nullable=False)


class UserRole(Base):
    __tablename__ = "user_roles"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False)
    role_id: Mapped[str] = mapped_column(ForeignKey("roles.id"), nullable=False)
    created_at: Mapped[str] = mapped_column(DateTime, nullable=False)


class LoanProduct(Base):
    __tablename__ = "loan_products"
    __table_args__ = (
        CheckConstraint(
            "(status = 'active' AND activated_at IS NOT NULL) OR (status != 'active')",
            name="ck_loan_product_active_state",
        ),
        CheckConstraint(
            "(status = 'retired' AND retired_at IS NOT NULL) OR (status != 'retired' AND retired_at IS NULL)",
            name="ck_loan_product_retired_state",
        ),
    )

    code: Mapped[str] = mapped_column(String(50), primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(30), default="draft", nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_by: Mapped[str | None] = mapped_column(ForeignKey("users.id"))
    activated_by: Mapped[str | None] = mapped_column(ForeignKey("users.id"))
    activated_at: Mapped[str | None] = mapped_column(DateTime)
    retired_by: Mapped[str | None] = mapped_column(ForeignKey("users.id"))
    retired_at: Mapped[str | None] = mapped_column(DateTime)
    created_at: Mapped[str] = mapped_column(DateTime, nullable=False)


class ProductWorkflow(Base):
    __tablename__ = "product_workflows"
    __table_args__ = (
        UniqueConstraint("product_code", "workflow_code", name="uq_product_workflow_code"),
        CheckConstraint(
            "(status = 'active' AND activated_at IS NOT NULL) OR (status != 'active')",
            name="ck_product_workflow_active_state",
        ),
        CheckConstraint(
            "(status = 'retired' AND retired_at IS NOT NULL) OR (status != 'retired' AND retired_at IS NULL)",
            name="ck_product_workflow_retired_state",
        ),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    product_code: Mapped[str] = mapped_column(ForeignKey("loan_products.code"), nullable=False)
    workflow_code: Mapped[str] = mapped_column(String(80), nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(30), default="draft", nullable=False)
    created_by: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False)
    activated_by: Mapped[str | None] = mapped_column(ForeignKey("users.id"))
    activated_at: Mapped[str | None] = mapped_column(DateTime)
    retired_by: Mapped[str | None] = mapped_column(ForeignKey("users.id"))
    retired_at: Mapped[str | None] = mapped_column(DateTime)
    created_at: Mapped[str] = mapped_column(DateTime, nullable=False)


class ProductVariable(Base):
    __tablename__ = "product_variables"
    __table_args__ = (UniqueConstraint("product_code", "variable_key", name="uq_product_variable_key"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    product_code: Mapped[str] = mapped_column(ForeignKey("loan_products.code"), nullable=False)
    variable_key: Mapped[str] = mapped_column(String(100), nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    business_meaning: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    data_type: Mapped[str] = mapped_column(String(50), nullable=False)
    is_required: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    allowed_sources: Mapped[str] = mapped_column(String(30), nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="draft", nullable=False)
    created_by: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False)
    activated_by: Mapped[str | None] = mapped_column(ForeignKey("users.id"))
    activated_at: Mapped[str | None] = mapped_column(DateTime)
    retired_by: Mapped[str | None] = mapped_column(ForeignKey("users.id"))
    retired_at: Mapped[str | None] = mapped_column(DateTime)
    created_at: Mapped[str] = mapped_column(DateTime, nullable=False)


class VariableCatalogVersion(Base):
    __tablename__ = "variable_catalog_versions"
    __table_args__ = (
        UniqueConstraint("product_code", "version_number", name="uq_catalog_product_version"),
        CheckConstraint(
            "(status = 'active' AND activated_at IS NOT NULL) OR (status != 'active')",
            name="ck_variable_catalog_active_state",
        ),
        CheckConstraint(
            "(status = 'retired' AND retired_at IS NOT NULL) OR (status != 'retired' AND retired_at IS NULL)",
            name="ck_variable_catalog_retired_state",
        ),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    product_code: Mapped[str] = mapped_column(ForeignKey("loan_products.code"), nullable=False)
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="draft", nullable=False)
    created_by: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False)
    activated_by: Mapped[str | None] = mapped_column(ForeignKey("users.id"))
    activated_at: Mapped[str | None] = mapped_column(DateTime)
    retired_by: Mapped[str | None] = mapped_column(ForeignKey("users.id"))
    retired_at: Mapped[str | None] = mapped_column(DateTime)
    created_at: Mapped[str] = mapped_column(DateTime, nullable=False)


class VariableCatalogItem(Base):
    __tablename__ = "variable_catalog_items"
    __table_args__ = (
        UniqueConstraint("catalog_version_id", "product_variable_id", name="uq_catalog_item_variable"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    catalog_version_id: Mapped[str] = mapped_column(
        ForeignKey("variable_catalog_versions.id"), nullable=False
    )
    product_variable_id: Mapped[str] = mapped_column(ForeignKey("product_variables.id"), nullable=False)
    is_required_in_runtime: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    default_value: Mapped[str | None] = mapped_column(Text)
    source_policy_payload: Mapped[str | None] = mapped_column(Text)


class ParameterSet(Base):
    __tablename__ = "parameter_sets"
    __table_args__ = (
        UniqueConstraint("product_code", "workflow_code", "version_number", name="uq_parameter_set_version"),
        CheckConstraint(
            "(status = 'active' AND activated_at IS NOT NULL) OR (status != 'active')",
            name="ck_parameter_set_active_state",
        ),
        CheckConstraint(
            "(status = 'retired' AND retired_at IS NOT NULL) OR (status != 'retired' AND retired_at IS NULL)",
            name="ck_parameter_set_retired_state",
        ),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    product_code: Mapped[str] = mapped_column(ForeignKey("loan_products.code"), nullable=False)
    workflow_code: Mapped[str] = mapped_column(String(80), nullable=False)
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="draft", nullable=False)
    payload: Mapped[str] = mapped_column(Text, nullable=False)
    created_by: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False)
    activated_by: Mapped[str | None] = mapped_column(ForeignKey("users.id"))
    activated_at: Mapped[str | None] = mapped_column(DateTime)
    retired_by: Mapped[str | None] = mapped_column(ForeignKey("users.id"))
    retired_at: Mapped[str | None] = mapped_column(DateTime)
    created_at: Mapped[str] = mapped_column(DateTime, nullable=False)


class RuleSet(Base):
    __tablename__ = "rule_sets"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    loan_product_code: Mapped[str] = mapped_column(ForeignKey("loan_products.code"), nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    effective_from: Mapped[str] = mapped_column(DateTime, nullable=False)
    effective_to: Mapped[str | None] = mapped_column(DateTime)
    status: Mapped[str] = mapped_column(String(30), default="draft", nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_by: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False)
    activated_by: Mapped[str | None] = mapped_column(ForeignKey("users.id"))
    activated_at: Mapped[str | None] = mapped_column(DateTime)
    retired_by: Mapped[str | None] = mapped_column(ForeignKey("users.id"))
    retired_at: Mapped[str | None] = mapped_column(DateTime)
    created_at: Mapped[str] = mapped_column(DateTime, nullable=False)


class RuleVersion(Base):
    __tablename__ = "rule_versions"
    __table_args__ = (UniqueConstraint("rule_set_id", "version_number", name="uq_rule_version_number"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    rule_set_id: Mapped[str] = mapped_column(ForeignKey("rule_sets.id"), nullable=False)
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    rule_key: Mapped[str] = mapped_column(String(100), nullable=False)
    rule_name: Mapped[str] = mapped_column(String(120), nullable=False)
    rule_type: Mapped[str] = mapped_column(String(50), nullable=False)
    condition_expression: Mapped[str] = mapped_column(Text, nullable=False)
    action_expression: Mapped[str] = mapped_column(Text, nullable=False)
    parameters: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(30), nullable=False)
    change_notes: Mapped[str | None] = mapped_column(Text)
    approved_by: Mapped[str | None] = mapped_column(ForeignKey("users.id"))
    created_by: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False)
    created_at: Mapped[str] = mapped_column(DateTime, nullable=False)


class PipelineStrategy(Base):
    __tablename__ = "pipeline_strategies"
    __table_args__ = (
        UniqueConstraint("loan_product_code", "version_number", name="uq_pipeline_strategy_version"),
        CheckConstraint(
            "(status IN ('draft', 'active', 'retired'))",
            name="ck_pipeline_strategy_status",
        ),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    loan_product_code: Mapped[str] = mapped_column(ForeignKey("loan_products.code"), nullable=False)
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    graph_definition: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False)
    approved_by: Mapped[str | None] = mapped_column(ForeignKey("users.id"))
    created_by: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False)
    created_at: Mapped[str] = mapped_column(DateTime, nullable=False)


class PipelineNode(Base):
    __tablename__ = "pipeline_nodes"
    __table_args__ = (
        UniqueConstraint("pipeline_strategy_id", "node_key", name="uq_pipeline_node_key"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    pipeline_strategy_id: Mapped[str] = mapped_column(ForeignKey("pipeline_strategies.id"), nullable=False)
    node_key: Mapped[str] = mapped_column(String(80), nullable=False)
    node_type: Mapped[str] = mapped_column(String(50), nullable=False)
    position_x: Mapped[int | None] = mapped_column(Integer)
    position_y: Mapped[int | None] = mapped_column(Integer)
    config_payload: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[str] = mapped_column(DateTime, nullable=False)


class WorkflowVersion(Base):
    __tablename__ = "workflow_versions"
    __table_args__ = (
        UniqueConstraint("workflow_id", "version_number", name="uq_workflow_version_number"),
        CheckConstraint(
            "(status = 'active' AND activated_at IS NOT NULL) OR (status != 'active')",
            name="ck_workflow_version_active_state",
        ),
        CheckConstraint(
            "(status = 'retired' AND retired_at IS NOT NULL) OR (status != 'retired' AND retired_at IS NULL)",
            name="ck_workflow_version_retired_state",
        ),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    workflow_id: Mapped[str] = mapped_column(ForeignKey("product_workflows.id"), nullable=False)
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="draft", nullable=False)
    variable_catalog_version_id: Mapped[str] = mapped_column(
        ForeignKey("variable_catalog_versions.id"), nullable=False
    )
    parameter_set_id: Mapped[str] = mapped_column(ForeignKey("parameter_sets.id"), nullable=False)
    pipeline_strategy_id: Mapped[str] = mapped_column(ForeignKey("pipeline_strategies.id"), nullable=False)
    change_notes: Mapped[str | None] = mapped_column(Text)
    created_by: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False)
    activated_by: Mapped[str | None] = mapped_column(ForeignKey("users.id"))
    activated_at: Mapped[str | None] = mapped_column(DateTime)
    retired_by: Mapped[str | None] = mapped_column(ForeignKey("users.id"))
    retired_at: Mapped[str | None] = mapped_column(DateTime)
    created_at: Mapped[str] = mapped_column(DateTime, nullable=False)


class WorkflowRuleAssignment(Base):
    __tablename__ = "workflow_rule_assignments"
    __table_args__ = (
        UniqueConstraint("workflow_version_id", "rule_version_id", name="uq_workflow_rule_assignment"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    workflow_version_id: Mapped[str] = mapped_column(ForeignKey("workflow_versions.id"), nullable=False)
    rule_version_id: Mapped[str] = mapped_column(ForeignKey("rule_versions.id"), nullable=False)
    execution_order: Mapped[int] = mapped_column(Integer, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class CreditRequest(Base):
    __tablename__ = "credit_requests"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    loan_product_code: Mapped[str] = mapped_column(ForeignKey("loan_products.code"), nullable=False)
    evaluation_id: Mapped[str | None] = mapped_column(ForeignKey("loan_evaluations.id"))
    workflow_code: Mapped[str | None] = mapped_column(String(80))
    document_type: Mapped[str] = mapped_column(String(20), nullable=False)
    document_number: Mapped[str] = mapped_column(String(30), nullable=False)
    campaign_code: Mapped[str] = mapped_column(String(80), nullable=False)
    requested_amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    comment: Mapped[str] = mapped_column(Text, nullable=False)
    customer_type: Mapped[str | None] = mapped_column(String(50))
    profile_code: Mapped[str | None] = mapped_column(String(50))
    segment_code: Mapped[str | None] = mapped_column(String(50))
    employment_status: Mapped[str | None] = mapped_column(String(50))
    validated_income: Mapped[float | None] = mapped_column(Numeric(12, 2))
    rci: Mapped[float | None] = mapped_column(Numeric(8, 4))
    offered_amount: Mapped[float | None] = mapped_column(Numeric(12, 2))
    installment_amount: Mapped[float | None] = mapped_column(Numeric(12, 2))
    term_months: Mapped[int | None] = mapped_column(Integer)
    rate: Mapped[float | None] = mapped_column(Numeric(8, 4))
    status: Mapped[str] = mapped_column(String(50), nullable=False)
    created_by: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False)
    created_at: Mapped[str] = mapped_column(DateTime, nullable=False)
    cancelled_at: Mapped[str | None] = mapped_column(DateTime)


class CreditRequestStatusHistory(Base):
    __tablename__ = "credit_request_status_history"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    request_id: Mapped[str] = mapped_column(ForeignKey("credit_requests.id"), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False)
    comment: Mapped[str | None] = mapped_column(Text)
    changed_by: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False)
    changed_at: Mapped[str] = mapped_column(DateTime, nullable=False)


class CreditRequestAttachment(Base):
    __tablename__ = "credit_request_attachments"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    request_id: Mapped[str] = mapped_column(ForeignKey("credit_requests.id"), nullable=False)
    storage_path: Mapped[str] = mapped_column(String(255), nullable=False)
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    mime_type: Mapped[str] = mapped_column(String(120), nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="active", nullable=False)
    uploaded_by: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False)
    uploaded_at: Mapped[str] = mapped_column(DateTime, nullable=False)


class LoanEvaluation(Base):
    __tablename__ = "loan_evaluations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    loan_product_code: Mapped[str] = mapped_column(ForeignKey("loan_products.code"), nullable=False)
    workflow_code: Mapped[str | None] = mapped_column(String(80))
    workflow_version_id: Mapped[str | None] = mapped_column(ForeignKey("workflow_versions.id"))
    variable_catalog_version_id: Mapped[str | None] = mapped_column(
        ForeignKey("variable_catalog_versions.id")
    )
    parameter_set_id: Mapped[str | None] = mapped_column(ForeignKey("parameter_sets.id"))
    document_type: Mapped[str] = mapped_column(String(20), nullable=False)
    document_number: Mapped[str] = mapped_column(String(30), nullable=False)
    campaign_code: Mapped[str] = mapped_column(String(80), nullable=False)
    rule_set_version: Mapped[str] = mapped_column(String(100), nullable=False)
    parameter_version: Mapped[str] = mapped_column(String(100), nullable=False)
    pipeline_version: Mapped[str] = mapped_column(String(100), nullable=False)
    decision_outcome: Mapped[str | None] = mapped_column(String(50))
    eligible: Mapped[bool | None] = mapped_column(Boolean)
    executed_by: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False)
    executed_at: Mapped[str] = mapped_column(DateTime, nullable=False)


class EvaluationInputSnapshot(Base):
    __tablename__ = "evaluation_input_snapshots"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    evaluation_id: Mapped[str] = mapped_column(ForeignKey("loan_evaluations.id"), nullable=False)
    source_type: Mapped[str] = mapped_column(String(50), nullable=False)
    source_key: Mapped[str] = mapped_column(String(100), nullable=False)
    field_name: Mapped[str] = mapped_column(String(100), nullable=False)
    field_value: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[str] = mapped_column(DateTime, nullable=False)


class DecisionTrace(Base):
    __tablename__ = "decision_traces"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    evaluation_id: Mapped[str] = mapped_column(ForeignKey("loan_evaluations.id"), nullable=False)
    pipeline_version: Mapped[str] = mapped_column(String(100), nullable=False)
    trace_payload: Mapped[str] = mapped_column(Text, nullable=False)
    human_summary: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[str] = mapped_column(DateTime, nullable=False)


class DecisionEvent(Base):
    __tablename__ = "decision_events"

    event_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    aggregate_id: Mapped[str] = mapped_column(String(36), nullable=False)
    aggregate_type: Mapped[str] = mapped_column(String(50), nullable=False)
    event_type: Mapped[str] = mapped_column(String(80), nullable=False)
    event_data: Mapped[str] = mapped_column(Text, nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    created_by: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False)
    created_at: Mapped[str] = mapped_column(DateTime, nullable=False)


class AdministrativeAuditEvent(Base):
    __tablename__ = "administrative_audit_events"

    event_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    aggregate_id: Mapped[str] = mapped_column(String(36), nullable=False)
    aggregate_type: Mapped[str] = mapped_column(String(50), nullable=False)
    event_type: Mapped[str] = mapped_column(String(80), nullable=False)
    event_payload: Mapped[str] = mapped_column(Text, nullable=False)
    created_by: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False)
    created_at: Mapped[str] = mapped_column(DateTime, nullable=False)


class AIPromptTemplate(Base):
    __tablename__ = "ai_prompt_templates"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    template_key: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    prompt_text: Mapped[str] = mapped_column(Text, nullable=False)
    product: Mapped[str | None] = mapped_column(String(50))
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_by: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False)
    created_at: Mapped[str] = mapped_column(DateTime, nullable=False)


class AIInteraction(Base):
    __tablename__ = "ai_interactions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False)
    evaluation_id: Mapped[str | None] = mapped_column(ForeignKey("loan_evaluations.id"))
    request_id: Mapped[str | None] = mapped_column(ForeignKey("credit_requests.id"))
    context_type: Mapped[str] = mapped_column(String(80), nullable=False)
    prompt_template_version: Mapped[str] = mapped_column(String(100), nullable=False)
    input_payload: Mapped[str] = mapped_column(Text, nullable=False)
    model_name: Mapped[str] = mapped_column(String(120), nullable=False)
    response_text: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[str] = mapped_column(DateTime, nullable=False)
