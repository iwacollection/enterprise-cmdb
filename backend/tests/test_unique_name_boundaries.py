from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.database.base import Base
from app.database.dependency import get_session
from app.main import app


def test_unique_name_boundaries_return_conflict():
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

    production = client.post(
        "/environments",
        headers=headers,
        json={"name": "production", "description": None},
    )
    assert production.status_code == 201

    duplicate_environment = client.post(
        "/environments",
        headers=headers,
        json={"name": "production", "description": "duplicate"},
    )
    assert duplicate_environment.status_code == 409
    assert duplicate_environment.json()["detail"] == "Environment name already exists"

    staging = client.post(
        "/environments",
        headers=headers,
        json={"name": "staging", "description": None},
    ).json()
    environment_update = client.put(
        f"/environments/{staging['id']}",
        headers=headers,
        json={"name": "production", "description": None},
    )
    assert environment_update.status_code == 409

    team = client.post(
        "/teams",
        headers=headers,
        json={"name": "platform", "description": None},
    )
    assert team.status_code == 201
    team_id = team.json()["id"]

    duplicate_team = client.post(
        "/teams",
        headers=headers,
        json={"name": "platform", "description": "duplicate"},
    )
    assert duplicate_team.status_code == 409
    assert duplicate_team.json()["detail"] == "Team name already exists"

    service = client.post(
        "/services",
        headers=headers,
        json={"name": "orders", "team_id": team_id, "description": None},
    )
    assert service.status_code == 201

    duplicate_service = client.post(
        "/services",
        headers=headers,
        json={"name": "orders", "team_id": team_id, "description": "duplicate"},
    )
    assert duplicate_service.status_code == 409
    assert duplicate_service.json()["detail"] == "Service name already exists"

    app.dependency_overrides.clear()
