from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.database.base import Base
from app.domain.audit.model import ChangeRecord
from app.domain.team.model import Team
from app.domain.team.repository import TeamRepository


def test_team_repository_crud_and_audit():
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        repository = TeamRepository(session)
        team = repository.create(
            Team(name="platform", description="platform team"),
            "request-create",
            "alice@example.com",
        )

        assert repository.get_by_id(team.id) is team
        assert repository.list() == [team]

        before = {"id": team.id, "name": team.name, "description": team.description}
        team.name = "sre"
        repository.update(team, before, "request-update", "bob@example.com")
        assert repository.get_by_id(team.id).name == "sre"

        team_id = team.id
        repository.delete(team, "request-delete", "carol@example.com")
        assert repository.get_by_id(team_id) is None

        changes = list(
            session.scalars(select(ChangeRecord).order_by(ChangeRecord.created_at)).all()
        )
        assert [change.action for change in changes] == ["create", "update", "delete"]
        assert [change.changed_by for change in changes] == [
            "alice@example.com",
            "bob@example.com",
            "carol@example.com",
        ]
        assert changes[1].before["name"] == "platform"
        assert changes[1].after["name"] == "sre"
        assert changes[2].before["id"] == team_id
        assert changes[2].after is None
