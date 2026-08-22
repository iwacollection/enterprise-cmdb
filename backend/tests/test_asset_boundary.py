from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.database.base import Base
from app.database.dependency import get_session
from app.main import app


def test_asset_rejects_missing_environment_reference():
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

    response = client.post(
        "/assets",
        headers={"X-CMDB-Actor": "boundary-test"},
        json={
            "name": "invalid-asset",
            "asset_type": "server",
            "environment_id": str(uuid4()),
            "team_id": "missing-team",
            "service_ids": [],
            "ips": [],
            "endpoints": [],
            "detail": {"cpu_cores": 2, "memory_mb": 4096, "disk_gb": 50},
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Environment not found"
    app.dependency_overrides.clear()
