from app.main import app


def test_health_route_registered():
    paths = {route.path for route in app.routes if hasattr(route, "path")}
    assert "/health" in paths
