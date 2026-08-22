from app.domain.team.model import Team
from app.domain.team.repository import TeamRepository
from app.domain.team.schema import TeamCreate


class TeamService:
    def __init__(self, repository: TeamRepository):
        self.repository = repository

    def list_teams(self) -> list[Team]:
        return self.repository.list()

    def get_team(self, team_id: str) -> Team | None:
        return self.repository.get_by_id(team_id)

    def create_team(self, data: TeamCreate) -> Team:
        return self.repository.create(
            Team(
                name=data.name,
                description=data.description,
            )
        )
