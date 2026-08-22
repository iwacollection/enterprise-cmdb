from app.domain.team.model import Team
from app.domain.team.repository import TeamRepository
from app.domain.team.schema import TeamCreate


class TeamService:
    def __init__(self, repository: TeamRepository):
        self.repository = repository

    def list_teams(self) -> list[Team]:
        return self.repository.list()

    def create_team(self, data: TeamCreate) -> Team:
        return self.repository.create(
            Team(
                name=data.name,
                description=data.description,
            )
        )
