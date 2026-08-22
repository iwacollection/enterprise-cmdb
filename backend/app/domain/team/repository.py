from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.team.model import Team


class TeamRepository:
    def __init__(self, session: Session):
        self.session = session

    def list(self) -> list[Team]:
        return list(self.session.scalars(select(Team)).all())

    def create(self, team: Team) -> Team:
        self.session.add(team)
        self.session.commit()
        self.session.refresh(team)
        return team
