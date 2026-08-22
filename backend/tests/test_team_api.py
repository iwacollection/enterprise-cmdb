from app.main import app


def test_team_routes_registered():
    routes = {
        (route.path, method)
        for route in app.routes
        if hasattr(route, "path")
        for method in getattr(route, "methods", set()) or set()
    }

    assert ("/teams", "GET") in routes
    assert ("/teams", "POST") in routes
    assert ("/teams/{team_id}", "GET") in routes
    assert ("/teams/{team_id}", "PUT") in routes
    assert ("/teams/{team_id}", "DELETE") in routes
