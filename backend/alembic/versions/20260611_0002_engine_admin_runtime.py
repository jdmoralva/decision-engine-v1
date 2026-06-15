"""engine admin runtime foundation

Revision ID: 20260611_0002
Revises: 20260607_0001
Create Date: 2026-06-11 00:02:00
"""

from alembic import op
import sqlalchemy as sa

from backend.app.infrastructure.db.base import Base
from backend.app.infrastructure.db import models  # noqa: F401


revision = "20260611_0002"
down_revision = "20260607_0001"
branch_labels = None
depends_on = None


def _column_names(table_name: str) -> set[str]:
    inspector = sa.inspect(op.get_bind())
    return {column["name"] for column in inspector.get_columns(table_name)}


def _table_names() -> set[str]:
    inspector = sa.inspect(op.get_bind())
    return set(inspector.get_table_names())


def _add_column_if_missing(table_name: str, column: sa.Column) -> None:
    if column.name in _column_names(table_name):
        return
    with op.batch_alter_table(table_name) as batch_op:
        batch_op.add_column(column)


def _create_table_if_missing(table_name: str) -> None:
    if table_name in _table_names():
        return
    Base.metadata.tables[table_name].create(bind=op.get_bind(), checkfirst=True)


def upgrade() -> None:
    _add_column_if_missing("loan_products", sa.Column("description", sa.Text(), nullable=True))
    _add_column_if_missing(
        "loan_products", sa.Column("status", sa.String(length=30), nullable=False, server_default="draft")
    )
    _add_column_if_missing("loan_products", sa.Column("created_by", sa.String(length=36), nullable=True))
    _add_column_if_missing("loan_products", sa.Column("activated_by", sa.String(length=36), nullable=True))
    _add_column_if_missing("loan_products", sa.Column("activated_at", sa.DateTime(), nullable=True))
    _add_column_if_missing("loan_products", sa.Column("retired_by", sa.String(length=36), nullable=True))
    _add_column_if_missing("loan_products", sa.Column("retired_at", sa.DateTime(), nullable=True))
    _add_column_if_missing("loan_products", sa.Column("deleted_by", sa.String(length=36), nullable=True))
    _add_column_if_missing("loan_products", sa.Column("deleted_at", sa.DateTime(), nullable=True))
    _add_column_if_missing("loan_products", sa.Column("delete_reason", sa.Text(), nullable=True))

    _add_column_if_missing("credit_requests", sa.Column("evaluation_id", sa.String(length=36), nullable=True))
    _add_column_if_missing("credit_requests", sa.Column("workflow_code", sa.String(length=80), nullable=True))

    _add_column_if_missing("loan_evaluations", sa.Column("workflow_code", sa.String(length=80), nullable=True))
    _add_column_if_missing(
        "loan_evaluations", sa.Column("workflow_version_id", sa.String(length=36), nullable=True)
    )
    _add_column_if_missing(
        "loan_evaluations", sa.Column("variable_catalog_version_id", sa.String(length=36), nullable=True)
    )
    _add_column_if_missing("loan_evaluations", sa.Column("parameter_set_id", sa.String(length=36), nullable=True))
    _add_column_if_missing("loan_evaluations", sa.Column("decision_outcome", sa.String(length=50), nullable=True))
    _add_column_if_missing("loan_evaluations", sa.Column("eligible", sa.Boolean(), nullable=True))

    _add_column_if_missing(
        "rule_sets", sa.Column("status", sa.String(length=30), nullable=False, server_default="draft")
    )
    _add_column_if_missing("rule_sets", sa.Column("activated_by", sa.String(length=36), nullable=True))
    _add_column_if_missing("rule_sets", sa.Column("activated_at", sa.DateTime(), nullable=True))
    _add_column_if_missing("rule_sets", sa.Column("retired_by", sa.String(length=36), nullable=True))
    _add_column_if_missing("rule_sets", sa.Column("retired_at", sa.DateTime(), nullable=True))
    _add_column_if_missing("rule_sets", sa.Column("deleted_by", sa.String(length=36), nullable=True))
    _add_column_if_missing("rule_sets", sa.Column("deleted_at", sa.DateTime(), nullable=True))
    _add_column_if_missing("rule_sets", sa.Column("delete_reason", sa.Text(), nullable=True))

    _add_column_if_missing("rule_versions", sa.Column("rule_key", sa.String(length=100), nullable=True))
    _add_column_if_missing("rule_versions", sa.Column("rule_name", sa.String(length=120), nullable=True))

    for table_name in (
        "permissions",
        "role_permissions",
        "product_workflows",
        "workflow_versions",
        "product_variables",
        "variable_catalog_versions",
        "variable_catalog_items",
        "parameter_sets",
        "workflow_rule_assignments",
        "credit_request_attachments",
        "administrative_audit_events",
    ):
        _create_table_if_missing(table_name)

    _add_column_if_missing("product_workflows", sa.Column("deleted_by", sa.String(length=36), nullable=True))
    _add_column_if_missing("product_workflows", sa.Column("deleted_at", sa.DateTime(), nullable=True))
    _add_column_if_missing("product_workflows", sa.Column("delete_reason", sa.Text(), nullable=True))


def downgrade() -> None:
    pass
