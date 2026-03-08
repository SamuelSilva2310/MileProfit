"""drop commission and bonuses from earnings

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-03-08
"""

from alembic import op
import sqlalchemy as sa

revision = "b2c3d4e5f6a7"
down_revision = "a1b2c3d4e5f6"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # SQLite doesn't support DROP COLUMN before 3.35 — use batch mode
    with op.batch_alter_table("earnings") as batch_op:
        batch_op.drop_column("commission")
        batch_op.drop_column("bonuses")


def downgrade() -> None:
    with op.batch_alter_table("earnings") as batch_op:
        batch_op.add_column(sa.Column("commission", sa.Float(), nullable=False, server_default="0.0"))
        batch_op.add_column(sa.Column("bonuses", sa.Float(), nullable=False, server_default="0.0"))
