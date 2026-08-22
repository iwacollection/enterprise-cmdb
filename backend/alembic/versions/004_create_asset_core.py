"""create asset core tables

Revision ID: 004_create_asset_core
Revises: 003_create_service
Create Date: 2026-08-22
"""

from alembic import op
import sqlalchemy as sa


revision = "004_create_asset_core"
down_revision = "003_create_service"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "assets",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("asset_type", sa.String(length=64), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("environment_id", sa.Uuid(), nullable=False),
        sa.Column("team_id", sa.String(length=36), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["environment_id"], ["environments.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["team_id"], ["teams.id"], ondelete="RESTRICT"),
    )
    op.create_index("ix_assets_asset_type", "assets", ["asset_type"])
    op.create_index("ix_assets_status", "assets", ["status"])
    op.create_index("ix_assets_environment_id", "assets", ["environment_id"])
    op.create_index("ix_assets_team_id", "assets", ["team_id"])

    op.create_table(
        "asset_services",
        sa.Column("asset_id", sa.String(length=36), nullable=False),
        sa.Column("service_id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["asset_id"], ["assets.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["service_id"], ["services.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("asset_id", "service_id"),
    )

    op.create_table(
        "asset_ips",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("asset_id", sa.String(length=36), nullable=False),
        sa.Column("address", sa.String(length=128), nullable=False),
        sa.Column("role", sa.String(length=64), nullable=True),
        sa.Column("is_primary", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["asset_id"], ["assets.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("asset_id", "address", name="uq_asset_ip"),
    )
    op.create_index("ix_asset_ips_asset_id", "asset_ips", ["asset_id"])

    op.create_table(
        "asset_endpoints",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("asset_id", sa.String(length=36), nullable=False),
        sa.Column("endpoint", sa.String(length=255), nullable=False),
        sa.Column("port", sa.Integer(), nullable=False),
        sa.Column("protocol", sa.String(length=32), nullable=True),
        sa.Column("role", sa.String(length=64), nullable=True),
        sa.Column("is_primary", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["asset_id"], ["assets.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("asset_id", "endpoint", "port", name="uq_asset_endpoint"),
    )
    op.create_index("ix_asset_endpoints_asset_id", "asset_endpoints", ["asset_id"])

    op.create_table(
        "compute_details",
        sa.Column("asset_id", sa.String(length=36), primary_key=True),
        sa.Column("cpu_cores", sa.Numeric(6, 2), nullable=True),
        sa.Column("memory_mb", sa.Integer(), nullable=True),
        sa.Column("disk_gb", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["asset_id"], ["assets.id"], ondelete="CASCADE"),
    )
    op.create_table(
        "database_details",
        sa.Column("asset_id", sa.String(length=36), primary_key=True),
        sa.Column("engine", sa.String(length=64), nullable=False),
        sa.Column("version", sa.String(length=64), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["asset_id"], ["assets.id"], ondelete="CASCADE"),
    )
    op.create_table(
        "redis_details",
        sa.Column("asset_id", sa.String(length=36), primary_key=True),
        sa.Column("version", sa.String(length=64), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["asset_id"], ["assets.id"], ondelete="CASCADE"),
    )
    op.create_table(
        "message_queue_details",
        sa.Column("asset_id", sa.String(length=36), primary_key=True),
        sa.Column("engine", sa.String(length=64), nullable=False),
        sa.Column("version", sa.String(length=64), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["asset_id"], ["assets.id"], ondelete="CASCADE"),
    )
    op.create_table(
        "kubernetes_cluster_details",
        sa.Column("asset_id", sa.String(length=36), primary_key=True),
        sa.Column("version", sa.String(length=64), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["asset_id"], ["assets.id"], ondelete="CASCADE"),
    )


def downgrade() -> None:
    op.drop_table("kubernetes_cluster_details")
    op.drop_table("message_queue_details")
    op.drop_table("redis_details")
    op.drop_table("database_details")
    op.drop_table("compute_details")
    op.drop_index("ix_asset_endpoints_asset_id", table_name="asset_endpoints")
    op.drop_table("asset_endpoints")
    op.drop_index("ix_asset_ips_asset_id", table_name="asset_ips")
    op.drop_table("asset_ips")
    op.drop_table("asset_services")
    op.drop_index("ix_assets_team_id", table_name="assets")
    op.drop_index("ix_assets_environment_id", table_name="assets")
    op.drop_index("ix_assets_status", table_name="assets")
    op.drop_index("ix_assets_asset_type", table_name="assets")
    op.drop_table("assets")
