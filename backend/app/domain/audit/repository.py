from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.audit.model import ChangeRecord


class ChangeRecordRepository:
    def __init__(self, session: Session):
        self.session = session

    def list(
        self,
        entity_type: str | None = None,
        entity_id: str | None = None,
        changed_by: str | None = None,
    ) -> list[ChangeRecord]:
        statement = select(ChangeRecord)
        if entity_type is not None:
            statement = statement.where(ChangeRecord.entity_type == entity_type)
        if entity_id is not None:
            statement = statement.where(ChangeRecord.entity_id == entity_id)
        if changed_by is not None:
            statement = statement.where(ChangeRecord.changed_by == changed_by)
        return list(self.session.scalars(statement.order_by(ChangeRecord.created_at.desc())).all())

    def get_by_id(self, change_id: str) -> ChangeRecord | None:
        return self.session.get(ChangeRecord, change_id)
