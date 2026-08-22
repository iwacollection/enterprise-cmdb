from app.main import app


def test_health_route_registered():
    paths = app.openapi()["paths"]
    assert "/health" in paths
    assert "get" in paths["/health"]
