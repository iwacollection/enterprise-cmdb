from datetime import datetime

from pydantic import BaseModel


class AssetRelationCreate(BaseModel):
    source_asset_id: str
    target_asset_id: str
    relation_type: str
    description: str | None = None


class AssetRelationResponse(BaseModel):
    id: str
    source_asset_id: str
    target_asset_id: str
    relation_type: str
    description: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
