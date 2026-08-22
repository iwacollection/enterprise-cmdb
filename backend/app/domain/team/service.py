from app.domain.team.model import Team
from app.domain.team.repository import TeamRepository
from app.domain.team.schema import TeamCreate, TeamUpdate


class TeamService:
    def __init__(self, repository: TeamRepository):
        self.repository = repository

    def list_teams(self) -> list[Team]:
        return self.repository.list()

    def get_team(self, team_id: str) -> Team | None:
        return self.repository.get_by_id(team_id)

    def create_team(self, data: TeamCreate, request_id: str, changed_by: str) -> Team:
        return self.repository.create(
            Team(
                name=data.name,
                description=data.description,
            ),
            request_id,
            changed_by,
        )

    def update_team(
        self,
        team: Team,
        data: TeamUpdate,
        request_id: str,
        changed_by: str,
    ) -> Team:
        before = {
            "id": team.id,
            "name": team.name,
            "description": team.description,
        }
        team.name = data.name
        team.description = data.description
        return self.repository.update(team, before, request_id, changed_by)

    def delete_team(self, team: Team, request_id: str, changed_by: str) -> None:
        self.repository.delete(team, request_id, changed_by)
