from app.domain.team.model import Team
from app.domain.team.schema import TeamCreate, TeamUpdate
from app.domain.team.service import TeamService


class FakeRepository:
    def __init__(self):
        self.team = None

    def list(self):
        return [] if self.team is None else [self.team]

    def get_by_id(self, team_id):
        if self.team is not None and self.team.id == team_id:
            return self.team
        return None

    def create(self, team):
        self.team = team
        return team

    def update(self, team):
        self.team = team
        return team

    def delete(self, team):
        self.team = None


def test_team_service_crud_contract():
    repository = FakeRepository()
    service = TeamService(repository)

    created = service.create_team(TeamCreate(name="platform", description="platform team"))
    created.id = "team-1"
    assert created.name == "platform"
    assert service.get_team("team-1") is created

    updated = service.update_team(
        created,
        TeamUpdate(name="sre", description="site reliability engineering"),
    )
    assert updated.name == "sre"
    assert updated.description == "site reliability engineering"

    service.delete_team(updated)
    assert service.get_team("team-1") is None
