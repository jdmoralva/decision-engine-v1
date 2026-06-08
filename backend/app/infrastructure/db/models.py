from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Numeric, String, Text
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


class UserRole(Base):
    __tablename__ = "user_roles"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False)
    role_id: Mapped[str] = mapped_column(ForeignKey("roles.id"), nullable=False)
    created_at: Mapped[str] = mapped_column(DateTime, nullable=False)


class LoanProduct(Base):
    __tablename__ = "loan_products"

    code: Mapped[str] = mapped_column(String(50), primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[str] = mapped_column(DateTime, nullable=False)


class CreditRequest(Base):
    __tablename__ = "credit_requests"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    loan_product_code: Mapped[str] = mapped_column(ForeignKey("loan_products.code"), nullable=False)
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


class LoanEvaluation(Base):
    __tablename__ = "loan_evaluations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    loan_product_code: Mapped[str] = mapped_column(ForeignKey("loan_products.code"), nullable=False)
    document_type: Mapped[str] = mapped_column(String(20), nullable=False)
    document_number: Mapped[str] = mapped_column(String(30), nullable=False)
    campaign_code: Mapped[str] = mapped_column(String(80), nullable=False)
    rule_set_version: Mapped[str] = mapped_column(String(100), nullable=False)
    parameter_version: Mapped[str] = mapped_column(String(100), nullable=False)
    pipeline_version: Mapped[str] = mapped_column(String(100), nullable=False)
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


class RuleSet(Base):
    __tablename__ = "rule_sets"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    loan_product_code: Mapped[str] = mapped_column(ForeignKey("loan_products.code"), nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    effective_from: Mapped[str] = mapped_column(DateTime, nullable=False)
    effective_to: Mapped[str | None] = mapped_column(DateTime)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_by: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False)
    created_at: Mapped[str] = mapped_column(DateTime, nullable=False)


class RuleVersion(Base):
    __tablename__ = "rule_versions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    rule_set_id: Mapped[str] = mapped_column(ForeignKey("rule_sets.id"), nullable=False)
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
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

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    pipeline_strategy_id: Mapped[str] = mapped_column(ForeignKey("pipeline_strategies.id"), nullable=False)
    node_key: Mapped[str] = mapped_column(String(80), nullable=False)
    node_type: Mapped[str] = mapped_column(String(50), nullable=False)
    position_x: Mapped[int | None] = mapped_column(Integer)
    position_y: Mapped[int | None] = mapped_column(Integer)
    config_payload: Mapped[str] = mapped_column(Text, nullable=False)
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
