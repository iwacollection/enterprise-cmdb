from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.domain.audit.model import ChangeRecord
from app.domain.relation.model import AssetRelation
from app.domain.relation.schema import AssetRelationCreate


class AssetRelationRepository:
    def __init__(self, session: Session):
        self.session = session

    def list_for_asset(self, asset_id: str, direction: str) -> list[AssetRelation]:
        statement = select(AssetRelation)
        if direction == "out":
            statement = statement.where(AssetRelation.source_asset_id == asset_id)
        elif direction == "in":
            statement = statement.where(AssetRelation.target_asset_id == asset_id)
        else:
            statement = statement.where(
                or_(
                    AssetRelation.source_asset_id == asset_id,
                    AssetRelation.target_asset_id == asset_id,
                )
            )
        return list(self.session.scalars(statement.order_by(AssetRelation.created_at)).all())

    def get_by_id(self, relation_id: str) -> AssetRelation | None:
        return self.session.get(AssetRelation, relation_id)

    def find_duplicate(self, data: AssetRelationCreate) -> AssetRelation | None:
        statement = select(AssetRelation).where(
            AssetRelation.source_asset_id == data.source_asset_id,
            AssetRelation.target_asset_id == data.target_asset_id,
            AssetRelation.relation_type == data.relation_type,
        )
        return self.session.scalar(statement)

    def create(
        self,
        data: AssetRelationCreate,
        request_id: str,
        changed_by: str,
    ) -> AssetRelation:
        relation = AssetRelation(**data.model_dump())
        self.session.add(relation)
        self.session.flush()
        self.session.add(
            ChangeRecord(
                request_id=request_id,
                entity_type="asset_relation",
                entity_id=relation.id,
                action="create",
                changed_by=changed_by,
                before=None,
                after=self._snapshot(relation),
            )
        )
        self.session.commit()
        self.session.refresh(relation)
        return relation

    def delete(self, relation: AssetRelation, request_id: str, changed_by: str) -> None:
        before = self._snapshot(relation)
        self.session.delete(relation)
        self.session.add(
            ChangeRecord(
                request_id=request_id,
                entity_type="asset_relation",
                entity_id=relation.id,
                action="delete",
                changed_by=changed_by,
                before=before,
                after=None,
            )
        )
        self.session.commit()

    @staticmethod
    def _snapshot(relation: AssetRelation) -> dict:
        return {
            "id": relation.id,
            "source_asset_id": relation.source_asset_id,
            "target_asset_id": relation.target_asset_id,
            "relation_type": relation.relation_type,
            "description": relation.description,
            "created_at": relation.created_at.isoformat(),
            "updated_at": relation.updated_at.isoformat(),
        }
