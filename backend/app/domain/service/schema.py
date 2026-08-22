from datetime import datetime

from pydantic import BaseModel


class ServiceCreate(BaseModel):
    name: str
    team_id: str
    description: str | None = None


class ServiceUpdate(BaseModel):
    name: str
    team_id: str
    description: str | None = None


class ServiceResponse(BaseModel):
    id: str
    name: str
    team_id: str
    description: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
