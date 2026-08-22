from app.domain.team.schema import TeamCreate


class FakeRepository:
    def create(self, team):
        return team


def test_team_service_create_contract():
    from app.domain.team.service import TeamService

    service = TeamService(FakeRepository())
    result = service.create_team(TeamCreate(name="platform", description="platform team"))

    assert result.name == "platform"
