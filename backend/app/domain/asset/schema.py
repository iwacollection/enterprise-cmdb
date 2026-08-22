from decimal import Decimal
from ipaddress import ip_interface
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


AssetType = Literal[
    "server",
    "virtual_machine",
    "database",
    "redis",
    "message_queue",
    "load_balancer",
    "kubernetes_cluster",
]
AssetStatus = Literal["active", "inactive"]


class ComputeDetailInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    cpu_cores: Decimal | None = Field(default=None, ge=0)
    memory_mb: int | None = Field(default=None, ge=0)
    disk_gb: int | None = Field(default=None, ge=0)


class DatabaseDetailInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    engine: str
    version: str | None = None


class RedisDetailInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    version: str | None = None


class MessageQueueDetailInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    engine: str
    version: str | None = None


class KubernetesClusterDetailInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    version: str | None = None


DETAIL_MODELS = {
    "server": ComputeDetailInput,
    "virtual_machine": ComputeDetailInput,
    "database": DatabaseDetailInput,
    "redis": RedisDetailInput,
    "message_queue": MessageQueueDetailInput,
    "kubernetes_cluster": KubernetesClusterDetailInput,
}


class AssetIPInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    address: str
    role: str | None = None
    is_primary: bool = False

    @field_validator("address")
    @classmethod
    def validate_address(cls, value: str) -> str:
        ip_interface(value)
        return value


class AssetEndpointInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    endpoint: str
    port: int = Field(ge=1, le=65535)
    protocol: str | None = None
    role: str | None = None
    is_primary: bool = False


class AssetWrite(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    asset_type: AssetType
    status: AssetStatus = "active"
    environment_id: UUID
    team_id: str
    description: str | None = None
    service_ids: list[str] = Field(default_factory=list)
    ips: list[AssetIPInput] = Field(default_factory=list)
    endpoints: list[AssetEndpointInput] = Field(default_factory=list)
    detail: dict | None = None

    @model_validator(mode="after")
    def validate_aggregate(self):
        detail_model = DETAIL_MODELS.get(self.asset_type)
        if detail_model is None:
            if self.detail is not None:
                raise ValueError(f"{self.asset_type} does not accept detail fields")
        elif self.detail is not None:
            detail_model.model_validate(self.detail)

        if len(self.service_ids) != len(set(self.service_ids)):
            raise ValueError("service_ids must not contain duplicates")
        if len(self.ips) != len({item.address for item in self.ips}):
            raise ValueError("ips must not contain duplicate addresses")
        endpoint_keys = {(item.endpoint, item.port) for item in self.endpoints}
        if len(self.endpoints) != len(endpoint_keys):
            raise ValueError("endpoints must not contain duplicate endpoint/port pairs")
        return self


class AssetCreate(AssetWrite):
    pass


class AssetUpdate(AssetWrite):
    pass


class AssetResponse(BaseModel):
    id: str
    name: str
    asset_type: str
    status: str
    environment_id: UUID
    team_id: str
    description: str | None
    service_ids: list[str]
    ips: list[dict]
    endpoints: list[dict]
    detail: dict | None
    created_at: str
    updated_at: str
