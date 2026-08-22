from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.database.base import Base
from app.domain.service.model import Service
from app.domain.service.repository import ServiceRepository
from app.domain.team.model import Team


def test_service_repository_crud():
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        team = Team(name="platform", description="platform team")
        session.add(team)
        session.commit()

        repository = ServiceRepository(session)
        service = repository.create(
            Service(name="cmdb-api", team_id=team.id, description="cmdb api")
        )

        assert repository.get_by_id(service.id) is service
        assert repository.list() == [service]

        service.name = "cmdb"
        repository.update(service)
        assert repository.get_by_id(service.id).name == "cmdb"

        repository.delete(service)
        assert repository.get_by_id(service.id) is None
