from datetime import datetime

from pydantic import BaseModel, Field


class ServiceCreate(BaseModel):
    name: str = Field(max_length=128)
    team_id: str = Field(max_length=36)
    description: str | None = None


class ServiceUpdate(BaseModel):
    name: str = Field(max_length=128)
    team_id: str = Field(max_length=36)
    description: str | None = None


class ServiceResponse(BaseModel):
    id: str
    name: str
    team_id: str
    description: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
