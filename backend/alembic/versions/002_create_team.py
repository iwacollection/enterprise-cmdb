"""create team table

Revision ID: 002_create_team
Revises: 001_create_environment
Create Date: 2026-08-22
"""

from alembic import op
import sqlalchemy as sa


revision = "002_create_team"
down_revision = "001_create_environment"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "teams",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("name", sa.String(length=128), nullable=False, unique=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("teams")
