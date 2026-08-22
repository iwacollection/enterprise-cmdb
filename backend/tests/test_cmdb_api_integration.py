from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.database.base import Base
from app.database.dependency import get_session
from app.main import app


def test_cmdb_core_api_flow():
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

    readiness = client.get("/ready")
    assert readiness.status_code == 200
    assert readiness.json() == {"status": "ready"}

    environment = client.post(
        "/environments",
        json={"name": "production", "description": "production environment"},
    )
    assert environment.status_code == 201
    environment_id = environment.json()["id"]

    team = client.post(
        "/teams",
        json={"name": "platform", "description": "platform team"},
    )
    assert team.status_code == 201
    team_id = team.json()["id"]

    service = client.post(
        "/services",
        json={"name": "orders", "team_id": team_id, "description": "order service"},
    )
    assert service.status_code == 201
    service_id = service.json()["id"]

    mysql = client.post(
        "/assets",
        headers={"X-CMDB-Actor": "integration-test"},
        json={
            "name": "mysql-prod",
            "asset_type": "database",
            "status": "active",
            "environment_id": environment_id,
            "team_id": team_id,
            "service_ids": [service_id],
            "ips": [{"address": "10.0.10.5/24", "is_primary": True}],
            "endpoints": [
                {
                    "endpoint": "mysql-prod.internal",
                    "port": 3306,
                    "protocol": "mysql",
                    "is_primary": True,
                }
            ],
            "detail": {"engine": "mysql", "version": "8.0"},
        },
    )
    assert mysql.status_code == 201, mysql.text
    mysql_id = mysql.json()["id"]
    assert mysql.json()["detail"] == {"engine": "mysql", "version": "8.0"}

    redis = client.post(
        "/assets",
        headers={"X-CMDB-Actor": "integration-test"},
        json={
            "name": "redis-prod",
            "asset_type": "redis",
            "status": "active",
            "environment_id": environment_id,
            "team_id": team_id,
            "service_ids": [service_id],
            "ips": [],
            "endpoints": [
                {
                    "endpoint": "redis-prod.internal",
                    "port": 6379,
                    "protocol": "redis",
                    "is_primary": True,
                }
            ],
            "detail": {"version": "7.2"},
        },
    )
    assert redis.status_code == 201, redis.text
    redis_id = redis.json()["id"]

    relation = client.post(
        "/relations",
        headers={"X-CMDB-Actor": "integration-test"},
        json={
            "source_asset_id": mysql_id,
            "target_asset_id": redis_id,
            "relation_type": "depends_on",
        },
    )
    assert relation.status_code == 201, relation.text

    relations = client.get(f"/assets/{mysql_id}/relations?direction=out")
    assert relations.status_code == 200
    assert len(relations.json()) == 1
    assert relations.json()[0]["target_asset_id"] == redis_id

    changes = client.get(f"/changes?entity_type=asset&entity_id={mysql_id}")
    assert changes.status_code == 200
    assert len(changes.json()) == 1
    assert changes.json()[0]["action"] == "create"
    assert changes.json()[0]["after"]["detail"]["engine"] == "mysql"

    app.dependency_overrides.clear()
