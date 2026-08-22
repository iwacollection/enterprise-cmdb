from app.domain.audit.model import ChangeRecord
from app.domain.audit.repository import ChangeRecordRepository


class ChangeRecordService:
    def __init__(self, repository: ChangeRecordRepository):
        self.repository = repository

    def list_changes(
        self,
        entity_type: str | None = None,
        entity_id: str | None = None,
        changed_by: str | None = None,
    ) -> list[ChangeRecord]:
        return self.repository.list(entity_type, entity_id, changed_by)

    def get_change(self, change_id: str) -> ChangeRecord | None:
        return self.repository.get_by_id(change_id)
