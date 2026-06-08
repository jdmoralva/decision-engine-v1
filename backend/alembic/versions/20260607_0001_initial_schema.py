"""initial schema

Revision ID: 20260607_0001
Revises:
Create Date: 2026-06-07 00:01:00
"""

from alembic import op

from backend.app.infrastructure.db.base import Base
from backend.app.infrastructure.db import models  # noqa: F401


revision = "20260607_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    Base.metadata.create_all(bind=bind)


def downgrade() -> None:
    bind = op.get_bind()
    Base.metadata.drop_all(bind=bind)
