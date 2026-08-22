from app.domain.team.schema import TeamCreate


def test_team_create_schema():
    team = TeamCreate(name="platform", description="platform team")

    assert team.name == "platform"
    assert team.description == "platform team"
