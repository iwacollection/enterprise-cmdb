from datetime import datetime

from pydantic import BaseModel, Field


class TeamCreate(BaseModel):
    name: str = Field(max_length=128)
    description: str | None = None


class TeamUpdate(BaseModel):
    name: str = Field(max_length=128)
    description: str | None = None


class TeamResponse(BaseModel):
    id: str
    name: str
    description: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
