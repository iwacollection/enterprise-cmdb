"""create environments table

Revision ID: 001_create_environment
"""

from alembic import op
import sqlalchemy as sa

revision = "001_create_environment"
down_revision = None


def upgrade():
    op.create_table(
        "environments",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("name", sa.String(length=128), nullable=False, unique=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )


def downgrade():
    op.drop_table("environments")
