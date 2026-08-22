from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.audit.model import ChangeRecord
from app.domain.team.model import Team


class TeamRepository:
    def __init__(self, session: Session):
        self.session = session

    def list(self) -> list[Team]:
        return list(self.session.scalars(select(Team)).all())

    def get_by_id(self, team_id: str) -> Team | None:
        return self.session.get(Team, team_id)

    def create(self, team: Team, request_id: str, changed_by: str) -> Team:
        self.session.add(team)
        self.session.flush()
        self.session.add(
            ChangeRecord(
                request_id=request_id,
                entity_type="team",
                entity_id=team.id,
                action="create",
                changed_by=changed_by,
                before=None,
                after=self._snapshot(team),
            )
        )
        self.session.commit()
        self.session.refresh(team)
        return team

    def update(self, team: Team, before: dict, request_id: str, changed_by: str) -> Team:
        self.session.add(
            ChangeRecord(
                request_id=request_id,
                entity_type="team",
                entity_id=team.id,
                action="update",
                changed_by=changed_by,
                before=before,
                after=self._snapshot(team),
            )
        )
        self.session.commit()
        self.session.refresh(team)
        return team

    def delete(self, team: Team, request_id: str, changed_by: str) -> None:
        before = self._snapshot(team)
        self.session.delete(team)
        self.session.add(
            ChangeRecord(
                request_id=request_id,
                entity_type="team",
                entity_id=team.id,
                action="delete",
                changed_by=changed_by,
                before=before,
                after=None,
            )
        )
        self.session.commit()

    @staticmethod
    def _snapshot(team: Team) -> dict:
        return {
            "id": team.id,
            "name": team.name,
            "description": team.description,
        }
