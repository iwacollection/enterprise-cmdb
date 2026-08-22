from datetime import datetime

from pydantic import BaseModel


class ChangeRecordResponse(BaseModel):
    id: str
    request_id: str
    entity_type: str
    entity_id: str
    action: str
    changed_by: str
    before: dict | None
    after: dict | None
    created_at: datetime

    model_config = {"from_attributes": True}
