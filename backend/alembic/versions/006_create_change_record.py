"""create change record table

Revision ID: 006_create_change_record
Revises: 005_create_asset_relation
Create Date: 2026-08-22
"""

from alembic import op
import sqlalchemy as sa


revision = "006_create_change_record"
down_revision = "005_create_asset_relation"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "change_records",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("request_id", sa.String(length=64), nullable=False),
        sa.Column("entity_type", sa.String(length=64), nullable=False),
        sa.Column("entity_id", sa.String(length=64), nullable=False),
        sa.Column("action", sa.String(length=32), nullable=False),
        sa.Column("changed_by", sa.String(length=255), nullable=False),
        sa.Column("before", sa.JSON(), nullable=True),
        sa.Column("after", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_change_records_request_id", "change_records", ["request_id"])
    op.create_index("ix_change_records_entity_type", "change_records", ["entity_type"])
    op.create_index("ix_change_records_entity_id", "change_records", ["entity_id"])
    op.create_index("ix_change_records_created_at", "change_records", ["created_at"])


def downgrade() -> None:
    op.drop_index("ix_change_records_created_at", table_name="change_records")
    op.drop_index("ix_change_records_entity_id", table_name="change_records")
    op.drop_index("ix_change_records_entity_type", table_name="change_records")
    op.drop_index("ix_change_records_request_id", table_name="change_records")
    op.drop_table("change_records")
