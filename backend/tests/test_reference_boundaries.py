from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.database.base import Base
from app.database.dependency import get_session
from app.main import app


def test_environment_team_and_service_reference_boundaries():
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)

    def override_session():
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_session] = override_session
    client = TestClient(app)
    headers = {"X-CMDB-Actor": "boundary-test"}

    missing_team = client.post(
        "/services",
        headers=headers,
        json={"name": "orphan", "team_id": "missing-team", "description": None},
    )
    assert missing_team.status_code == 404
    assert missing_team.json()["detail"] == "Team not found"

    environment = client.post(
        "/environments",
        headers=headers,
        json={"name": "production", "description": None},
    ).json()
    team = client.post(
        "/teams",
        headers=headers,
        json={"name": "platform", "description": None},
    ).json()
    service = client.post(
        "/services",
        headers=headers,
        json={"name": "orders", "team_id": team["id"], "description": None},
    ).json()

    asset = client.post(
        "/assets",
        headers=headers,
        json={
            "name": "orders-db",
            "asset_type": "database",
            "environment_id": environment["id"],
            "team_id": team["id"],
            "service_ids": [service["id"]],
            "ips": [],
            "endpoints": [],
            "detail": {"engine": "postgresql", "version": "16"},
        },
    )
    assert asset.status_code == 201, asset.text

    environment_delete = client.delete(
        f"/environments/{environment['id']}", headers=headers
    )
    assert environment_delete.status_code == 409
    assert environment_delete.json()["detail"] == "Environment is still referenced by assets"

    service_delete = client.delete(f"/services/{service['id']}", headers=headers)
    assert service_delete.status_code == 409
    assert service_delete.json()["detail"] == "Service is still referenced by assets"

    team_delete = client.delete(f"/teams/{team['id']}", headers=headers)
    assert team_delete.status_code == 409
    assert team_delete.json()["detail"] == "Team is still referenced"

    app.dependency_overrides.clear()
