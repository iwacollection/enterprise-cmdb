from fastapi.testclient import TestClient

from app.main import app


def test_web_console_redirects_to_ui():
    client = TestClient(app, follow_redirects=False)
    response = client.get("/")

    assert response.status_code in {302, 307}
    assert response.headers["location"] == "/ui/"


def test_web_console_index_is_served():
    client = TestClient(app)
    response = client.get("/ui/")

    assert response.status_code == 200
    assert "Enterprise CMDB" in response.text
