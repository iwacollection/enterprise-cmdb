"""create asset relation table

Revision ID: 005_create_asset_relation
Revises: 004_create_asset_core
Create Date: 2026-08-22
"""

from alembic import op
import sqlalchemy as sa


revision = "005_create_asset_relation"
down_revision = "004_create_asset_core"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "asset_relations",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("source_asset_id", sa.String(length=36), nullable=False),
        sa.Column("target_asset_id", sa.String(length=36), nullable=False),
        sa.Column("relation_type", sa.String(length=64), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["source_asset_id"], ["assets.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["target_asset_id"], ["assets.id"], ondelete="RESTRICT"),
        sa.UniqueConstraint(
            "source_asset_id",
            "target_asset_id",
            "relation_type",
            name="uq_asset_relation",
        ),
    )
    op.create_index("ix_asset_relations_source_asset_id", "asset_relations", ["source_asset_id"])
    op.create_index("ix_asset_relations_target_asset_id", "asset_relations", ["target_asset_id"])
    op.create_index("ix_asset_relations_relation_type", "asset_relations", ["relation_type"])


def downgrade() -> None:
    op.drop_index("ix_asset_relations_relation_type", table_name="asset_relations")
    op.drop_index("ix_asset_relations_target_asset_id", table_name="asset_relations")
    op.drop_index("ix_asset_relations_source_asset_id", table_name="asset_relations")
    op.drop_table("asset_relations")
