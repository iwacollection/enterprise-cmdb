from app.domain.relation.model import AssetRelation
from app.domain.relation.repository import AssetRelationRepository
from app.domain.relation.schema import AssetRelationCreate


class AssetRelationService:
    def __init__(self, repository: AssetRelationRepository):
        self.repository = repository

    def asset_exists(self, asset_id: str) -> bool:
        return self.repository.asset_exists(asset_id)

    def list_relations(self, asset_id: str, direction: str) -> list[AssetRelation]:
        return self.repository.list_for_asset(asset_id, direction)

    def get_relation(self, relation_id: str) -> AssetRelation | None:
        return self.repository.get_by_id(relation_id)

    def relation_exists(self, data: AssetRelationCreate) -> bool:
        return self.repository.find_duplicate(data) is not None

    def create_relation(
        self,
        data: AssetRelationCreate,
        request_id: str,
        changed_by: str,
    ) -> AssetRelation:
        return self.repository.create(data, request_id, changed_by)

    def delete_relation(
        self,
        relation: AssetRelation,
        request_id: str,
        changed_by: str,
    ) -> None:
        self.repository.delete(relation, request_id, changed_by)
