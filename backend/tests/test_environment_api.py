from app.main import app


def test_environment_route_registered():
    paths = app.openapi()["paths"]
    assert "/environments" in paths
    assert "get" in paths["/environments"]
    assert "post" in paths["/environments"]
