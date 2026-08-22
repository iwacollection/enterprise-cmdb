import base64
import json
from types import SimpleNamespace

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.api import auth
from app.database.base import Base
from app.database.dependency import get_session
from app.main import app


def easy_auth_header(object_id: str, roles: list[str]) -> dict[str, str]:
    payload = {
        "auth_typ": "aad",
        "name_typ": "name",
        "role_typ": "roles",
        "claims": [
            {"typ": "name", "val": "operator@example.com"},
            {
                "typ": "http://schemas.microsoft.com/identity/claims/objectidentifier",
                "val": object_id,
            },
            *[{"typ": "roles", "val": role} for role in roles],
        ],
    }
    encoded = base64.b64encode(json.dumps(payload).encode()).decode()
    return {"X-MS-CLIENT-PRINCIPAL": encoded}


def test_entra_rbac_and_audit_actor(monkeypatch):
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
    monkeypatch.setattr(auth, "settings", SimpleNamespace(auth_mode="entra"))
    client = TestClient(app)

    no_identity = client.get("/environments")
    assert no_identity.status_code == 401

    reader_headers = easy_auth_header("reader-object-id", [auth.READER_ROLE])
    reader_list = client.get("/environments", headers=reader_headers)
    assert reader_list.status_code == 200

    reader_write = client.post(
        "/environments",
        headers=reader_headers,
        json={"name": "production", "description": "prod"},
    )
    assert reader_write.status_code == 403

    admin_headers = easy_auth_header("admin-object-id", [auth.ADMIN_ROLE])
    admin_write = client.post(
        "/environments",
        headers=admin_headers,
        json={"name": "production", "description": "prod"},
    )
    assert admin_write.status_code == 201

    changes = client.get("/changes", headers=reader_headers)
    assert changes.status_code == 200
    assert changes.json()[0]["changed_by"] == "admin-object-id"

    app.dependency_overrides.clear()
