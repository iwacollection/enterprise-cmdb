from decimal import Decimal
from uuid import uuid4

import pytest
from pydantic import ValidationError

from app.domain.asset.schema import AssetCreate
from app.domain.environment.schema import EnvironmentCreate
from app.domain.relation.schema import AssetRelationCreate
from app.domain.service.schema import ServiceCreate
from app.domain.team.schema import TeamCreate
from app.main import app


def test_core_names_reject_values_larger_than_database_columns():
    with pytest.raises(ValidationError):
        EnvironmentCreate(name="e" * 129)
    with pytest.raises(ValidationError):
        TeamCreate(name="t" * 129)
    with pytest.raises(ValidationError):
        ServiceCreate(name="s" * 129, team_id="team-1")


def test_asset_rejects_database_column_overflow_at_input_boundary():
    base = {
        "name": "compute-1",
        "asset_type": "server",
        "environment_id": str(uuid4()),
        "team_id": "team-1",
        "service_ids": [],
        "ips": [],
        "endpoints": [],
    }

    with pytest.raises(ValidationError):
        AssetCreate(**{**base, "name": "a" * 256})
    with pytest.raises(ValidationError):
        AssetCreate(**{**base, "team_id": "t" * 37})
    with pytest.raises(ValidationError):
        AssetCreate(**{**base, "detail": {"cpu_cores": Decimal("10000.00")}})
    with pytest.raises(ValidationError):
        AssetCreate(**{**base, "detail": {"memory_mb": 2147483648}})


def test_relation_type_rejects_values_larger_than_database_column():
    with pytest.raises(ValidationError):
        AssetRelationCreate(
            source_asset_id="asset-1",
            target_asset_id="asset-2",
            relation_type="r" * 65,
        )


def test_audit_header_limits_are_part_of_openapi_contract():
    operation = app.openapi()["paths"]["/environments"]["post"]
    parameters = {parameter["name"]: parameter for parameter in operation["parameters"]}

    actor_schema = parameters["X-CMDB-Actor"]["schema"]
    actor_string_schema = next(item for item in actor_schema["anyOf"] if item.get("type") == "string")
    assert actor_string_schema["maxLength"] == 255

    request_id_schema = parameters["X-Request-ID"]["schema"]
    request_id_string_schema = next(
        item for item in request_id_schema["anyOf"] if item.get("type") == "string"
    )
    assert request_id_string_schema["maxLength"] == 64
