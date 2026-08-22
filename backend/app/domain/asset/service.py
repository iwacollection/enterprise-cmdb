from uuid import UUID

from app.domain.asset.repository import AssetRepository
from app.domain.asset.schema import AssetCreate, AssetUpdate, AssetWrite


class AssetService:
    def __init__(self, repository: AssetRepository):
        self.repository = repository

    def reference_error(self, data: AssetWrite) -> str | None:
        return self.repository.reference_error(data)

    def list_assets(
        self,
        name: str | None = None,
        asset_type: str | None = None,
        status: str | None = None,
        environment_id: UUID | None = None,
        team_id: str | None = None,
        service_id: str | None = None,
    ) -> list[dict]:
        return self.repository.list(
            name=name,
            asset_type=asset_type,
            status=status,
            environment_id=environment_id,
            team_id=team_id,
            service_id=service_id,
        )

    def get_asset(self, asset_id: str) -> dict | None:
        return self.repository.get_by_id(asset_id)

    def create_asset(self, data: AssetCreate, request_id: str, changed_by: str) -> dict:
        return self.repository.create(data, request_id, changed_by)

    def update_asset(
        self,
        asset_id: str,
        data: AssetUpdate,
        request_id: str,
        changed_by: str,
    ) -> dict | None:
        return self.repository.update(asset_id, data, request_id, changed_by)
