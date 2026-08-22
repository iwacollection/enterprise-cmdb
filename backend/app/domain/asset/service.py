from app.domain.asset.repository import AssetRepository
from app.domain.asset.schema import AssetCreate, AssetUpdate


class AssetService:
    def __init__(self, repository: AssetRepository):
        self.repository = repository

    def list_assets(self) -> list[dict]:
        return self.repository.list()

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
