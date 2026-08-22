from app.main import app


def test_environment_route_registered():
    paths = {route.path for route in app.routes if hasattr(route, "path")}
    assert "/environments" in paths
