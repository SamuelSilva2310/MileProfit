"""add vehicles table and earning notes/is_paid/vehicle_id fields

Revision ID: c3d4e5f6a7b8
Revises: b2c3d4e5f6a7
Create Date: 2026-04-30
"""

from alembic import op
import sqlalchemy as sa

revision = "c3d4e5f6a7b8"
down_revision = "b2c3d4e5f6a7"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "vehicles",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_vehicles_user_id", "vehicles", ["user_id"])

    with op.batch_alter_table("earnings") as batch_op:
        batch_op.add_column(sa.Column("vehicle_id", sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column("notes", sa.Text(), nullable=True))
        batch_op.add_column(sa.Column("is_paid", sa.Boolean(), nullable=False, server_default="1"))

    with op.batch_alter_table("activities") as batch_op:
        batch_op.add_column(sa.Column("vehicle_id", sa.Integer(), nullable=True))

    with op.batch_alter_table("expenses") as batch_op:
        batch_op.add_column(sa.Column("vehicle_id", sa.Integer(), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table("expenses") as batch_op:
        batch_op.drop_column("vehicle_id")

    with op.batch_alter_table("activities") as batch_op:
        batch_op.drop_column("vehicle_id")

    with op.batch_alter_table("earnings") as batch_op:
        batch_op.drop_column("is_paid")
        batch_op.drop_column("notes")
        batch_op.drop_column("vehicle_id")

    op.drop_index("ix_vehicles_user_id", "vehicles")
    op.drop_table("vehicles")
