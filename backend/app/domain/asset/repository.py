from decimal import Decimal
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.domain.asset.model import (
    Asset,
    AssetEndpoint,
    AssetIP,
    AssetService,
    ComputeDetail,
    DatabaseDetail,
    KubernetesClusterDetail,
    MessageQueueDetail,
    RedisDetail,
)
from app.domain.asset.schema import AssetWrite
from app.domain.audit.model import ChangeRecord
from app.domain.environment.model import Environment
from app.domain.service.model import Service
from app.domain.team.model import Team


DETAIL_MODELS = {
    "server": ComputeDetail,
    "virtual_machine": ComputeDetail,
    "database": DatabaseDetail,
    "redis": RedisDetail,
    "message_queue": MessageQueueDetail,
    "kubernetes_cluster": KubernetesClusterDetail,
}
ALL_DETAIL_MODELS = tuple(set(DETAIL_MODELS.values()))


class AssetRepository:
    def __init__(self, session: Session):
        self.session = session

    def reference_error(self, data: AssetWrite) -> str | None:
        if self.session.get(Environment, data.environment_id) is None:
            return "Environment not found"
        if self.session.get(Team, data.team_id) is None:
            return "Team not found"
        if data.service_ids:
            existing = set(
                self.session.scalars(
                    select(Service.id).where(Service.id.in_(data.service_ids))
                ).all()
            )
            missing = [service_id for service_id in data.service_ids if service_id not in existing]
            if missing:
                return f"Service not found: {missing[0]}"
        return None

    def list(
        self,
        name: str | None = None,
        asset_type: str | None = None,
        status: str | None = None,
        environment_id: UUID | None = None,
        team_id: str | None = None,
        service_id: str | None = None,
    ) -> list[dict]:
        statement = select(Asset)
        if service_id is not None:
            statement = statement.join(AssetService).where(AssetService.service_id == service_id)
        if name is not None:
            statement = statement.where(Asset.name.ilike(f"%{name}%"))
        if asset_type is not None:
            statement = statement.where(Asset.asset_type == asset_type)
        if status is not None:
            statement = statement.where(Asset.status == status)
        if environment_id is not None:
            statement = statement.where(Asset.environment_id == environment_id)
        if team_id is not None:
            statement = statement.where(Asset.team_id == team_id)
        assets = self.session.scalars(statement.distinct().order_by(Asset.name)).all()
        return [self._snapshot(asset) for asset in assets]

    def get_by_id(self, asset_id: str) -> dict | None:
        asset = self.session.get(Asset, asset_id)
        return None if asset is None else self._snapshot(asset)

    def create(
        self,
        data: AssetWrite,
        request_id: str,
        changed_by: str,
    ) -> dict:
        asset = Asset(
            name=data.name,
            asset_type=data.asset_type,
            status=data.status,
            environment_id=data.environment_id,
            team_id=data.team_id,
            description=data.description,
        )
        self.session.add(asset)
        self.session.flush()
        self._replace_children(asset, data)
        self.session.flush()

        after = self._snapshot(asset)
        self.session.add(
            ChangeRecord(
                request_id=request_id,
                entity_type="asset",
                entity_id=asset.id,
                action="create",
                changed_by=changed_by,
                before=None,
                after=after,
            )
        )
        self.session.commit()
        return after

    def update(
        self,
        asset_id: str,
        data: AssetWrite,
        request_id: str,
        changed_by: str,
    ) -> dict | None:
        asset = self.session.get(Asset, asset_id)
        if asset is None:
            return None

        before = self._snapshot(asset)
        asset.name = data.name
        asset.asset_type = data.asset_type
        asset.status = data.status
        asset.environment_id = data.environment_id
        asset.team_id = data.team_id
        asset.description = data.description

        self._replace_children(asset, data)
        self.session.flush()
        after = self._snapshot(asset)
        self.session.add(
            ChangeRecord(
                request_id=request_id,
                entity_type="asset",
                entity_id=asset.id,
                action="update",
                changed_by=changed_by,
                before=before,
                after=after,
            )
        )
        self.session.commit()
        return after

    def _replace_children(self, asset: Asset, data: AssetWrite) -> None:
        self.session.execute(delete(AssetService).where(AssetService.asset_id == asset.id))
        self.session.execute(delete(AssetIP).where(AssetIP.asset_id == asset.id))
        self.session.execute(delete(AssetEndpoint).where(AssetEndpoint.asset_id == asset.id))
        for detail_model in ALL_DETAIL_MODELS:
            self.session.execute(delete(detail_model).where(detail_model.asset_id == asset.id))

        self.session.add_all(
            [AssetService(asset_id=asset.id, service_id=service_id) for service_id in data.service_ids]
        )
        self.session.add_all(
            [
                AssetIP(
                    asset_id=asset.id,
                    address=item.address,
                    role=item.role,
                    is_primary=item.is_primary,
                )
                for item in data.ips
            ]
        )
        self.session.add_all(
            [
                AssetEndpoint(
                    asset_id=asset.id,
                    endpoint=item.endpoint,
                    port=item.port,
                    protocol=item.protocol,
                    role=item.role,
                    is_primary=item.is_primary,
                )
                for item in data.endpoints
            ]
        )

        detail_model = DETAIL_MODELS.get(data.asset_type)
        if detail_model is not None and data.detail is not None:
            self.session.add(detail_model(asset_id=asset.id, **data.detail))

    def _snapshot(self, asset: Asset) -> dict:
        service_ids = list(
            self.session.scalars(
                select(AssetService.service_id).where(AssetService.asset_id == asset.id)
            ).all()
        )
        ips = self.session.scalars(
            select(AssetIP).where(AssetIP.asset_id == asset.id).order_by(AssetIP.address)
        ).all()
        endpoints = self.session.scalars(
            select(AssetEndpoint)
            .where(AssetEndpoint.asset_id == asset.id)
            .order_by(AssetEndpoint.endpoint, AssetEndpoint.port)
        ).all()

        detail = None
        detail_model = DETAIL_MODELS.get(asset.asset_type)
        if detail_model is not None:
            detail_row = self.session.get(detail_model, asset.id)
            if detail_row is not None:
                detail = {
                    column.name: self._json_value(getattr(detail_row, column.name))
                    for column in detail_row.__table__.columns
                    if column.name not in {"asset_id", "created_at", "updated_at"}
                }

        return {
            "id": asset.id,
            "name": asset.name,
            "asset_type": asset.asset_type,
            "status": asset.status,
            "environment_id": str(asset.environment_id),
            "team_id": asset.team_id,
            "description": asset.description,
            "service_ids": service_ids,
            "ips": [
                {
                    "id": item.id,
                    "address": item.address,
                    "role": item.role,
                    "is_primary": item.is_primary,
                }
                for item in ips
            ],
            "endpoints": [
                {
                    "id": item.id,
                    "endpoint": item.endpoint,
                    "port": item.port,
                    "protocol": item.protocol,
                    "role": item.role,
                    "is_primary": item.is_primary,
                }
                for item in endpoints
            ],
            "detail": detail,
            "created_at": asset.created_at.isoformat(),
            "updated_at": asset.updated_at.isoformat(),
        }

    @staticmethod
    def _json_value(value):
        if hasattr(value, "isoformat"):
            return value.isoformat()
        if isinstance(value, Decimal):
            return float(value)
        return value
