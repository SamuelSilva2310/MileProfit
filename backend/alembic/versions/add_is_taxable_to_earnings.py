"""add is_taxable to earnings

Revision ID: a1b2c3d4e5f6
Revises: 0079768a066e
Create Date: 2026-03-08
"""

from alembic import op
import sqlalchemy as sa

revision = "a1b2c3d4e5f6"
down_revision = "0079768a066e"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "earnings",
        sa.Column("is_taxable", sa.Boolean(), nullable=False, server_default="1"),
    )


def downgrade() -> None:
    op.drop_column("earnings", "is_taxable")
