from app.main import app


def test_service_routes_registered():
    paths = app.openapi()["paths"]

    assert "get" in paths["/services"]
    assert "post" in paths["/services"]
    assert "get" in paths["/services/{service_id}"]
    assert "put" in paths["/services/{service_id}"]
    assert "delete" in paths["/services/{service_id}"]
