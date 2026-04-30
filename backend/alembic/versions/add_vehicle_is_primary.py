"""add is_primary to vehicles

Revision ID: d4e5f6a7b8c9
Revises: c3d4e5f6a7b8
Create Date: 2026-04-30
"""

from alembic import op
import sqlalchemy as sa

revision = "d4e5f6a7b8c9"
down_revision = "c3d4e5f6a7b8"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("vehicles") as batch_op:
        batch_op.add_column(sa.Column("is_primary", sa.Boolean(), nullable=False, server_default="0"))


def downgrade() -> None:
    with op.batch_alter_table("vehicles") as batch_op:
        batch_op.drop_column("is_primary")
