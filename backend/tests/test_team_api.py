from app.main import app


def test_team_routes_registered():
    paths = app.openapi()["paths"]

    assert "get" in paths["/teams"]
    assert "post" in paths["/teams"]
    assert "get" in paths["/teams/{team_id}"]
    assert "put" in paths["/teams/{team_id}"]
    assert "delete" in paths["/teams/{team_id}"]
