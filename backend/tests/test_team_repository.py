from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.database.base import Base
from app.domain.team.model import Team
from app.domain.team.repository import TeamRepository


def test_team_repository_crud():
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        repository = TeamRepository(session)
        team = repository.create(Team(name="platform", description="platform team"))

        assert repository.get_by_id(team.id) is team
        assert repository.list() == [team]

        team.name = "sre"
        repository.update(team)
        assert repository.get_by_id(team.id).name == "sre"

        repository.delete(team)
        assert repository.get_by_id(team.id) is None
