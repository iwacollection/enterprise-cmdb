from app.main import app


def test_service_routes_registered():
    routes = {(route.path, method) for route in app.routes for method in route.methods or set()}

    assert ("/services", "GET") in routes
    assert ("/services", "POST") in routes
    assert ("/services/{service_id}", "GET") in routes
    assert ("/services/{service_id}", "PUT") in routes
    assert ("/services/{service_id}", "DELETE") in routes
