"""create service table

Revision ID: 003_create_service
Revises: 002_create_team
Create Date: 2026-08-22
"""

from alembic import op
import sqlalchemy as sa


revision = "003_create_service"
down_revision = "002_create_team"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "services",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("name", sa.String(length=128), nullable=False, unique=True),
        sa.Column("team_id", sa.String(length=36), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["team_id"], ["teams.id"], ondelete="RESTRICT"),
    )


def downgrade() -> None:
    op.drop_table("services")
