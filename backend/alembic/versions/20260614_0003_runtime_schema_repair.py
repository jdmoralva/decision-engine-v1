"""runtime schema repair for legacy SQLite databases

Revision ID: 20260614_0003
Revises: 20260611_0002
Create Date: 2026-06-14 00:03:00
"""

from alembic import op
import sqlalchemy as sa


revision = "20260614_0003"
down_revision = "20260611_0002"
branch_labels = None
depends_on = None


def _column_names(table_name: str) -> set[str]:
    inspector = sa.inspect(op.get_bind())
    return {column["name"] for column in inspector.get_columns(table_name)}


def _add_column_if_missing(table_name: str, column: sa.Column) -> None:
    if column.name in _column_names(table_name):
        return
    with op.batch_alter_table(table_name) as batch_op:
        batch_op.add_column(column)


def upgrade() -> None:
    # Repair legacy local databases that were stamped to 0002 before the
    # runtime-admin columns were actually present.
    for table_name in ("loan_products", "rule_sets", "product_workflows"):
        _add_column_if_missing(table_name, sa.Column("deleted_by", sa.String(length=36), nullable=True))
        _add_column_if_missing(table_name, sa.Column("deleted_at", sa.DateTime(), nullable=True))
        _add_column_if_missing(table_name, sa.Column("delete_reason", sa.Text(), nullable=True))


def downgrade() -> None:
    pass
