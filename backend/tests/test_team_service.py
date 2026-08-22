from app.domain.team.schema import TeamCreate, TeamUpdate
from app.domain.team.service import TeamService


class FakeRepository:
    def __init__(self):
        self.team = None
        self.audit = []

    def list(self):
        return [] if self.team is None else [self.team]

    def get_by_id(self, team_id):
        if self.team is not None and self.team.id == team_id:
            return self.team
        return None

    def create(self, team, request_id, changed_by):
        self.team = team
        self.audit.append(("create", request_id, changed_by))
        return team

    def update(self, team, before, request_id, changed_by):
        self.team = team
        self.audit.append(("update", request_id, changed_by, before))
        return team

    def delete(self, team, request_id, changed_by):
        self.audit.append(("delete", request_id, changed_by))
        self.team = None


def test_team_service_crud_contract():
    repository = FakeRepository()
    service = TeamService(repository)

    created = service.create_team(
        TeamCreate(name="platform", description="platform team"),
        "request-create",
        "alice@example.com",
    )
    created.id = "team-1"
    assert created.name == "platform"
    assert service.get_team("team-1") is created

    updated = service.update_team(
        created,
        TeamUpdate(name="sre", description="site reliability engineering"),
        "request-update",
        "bob@example.com",
    )
    assert updated.name == "sre"
    assert updated.description == "site reliability engineering"

    service.delete_team(updated, "request-delete", "carol@example.com")
    assert service.get_team("team-1") is None
    assert [entry[0] for entry in repository.audit] == ["create", "update", "delete"]
