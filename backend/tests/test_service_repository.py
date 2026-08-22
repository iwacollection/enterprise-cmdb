from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.database.base import Base
from app.domain.audit.model import ChangeRecord
from app.domain.service.model import Service
from app.domain.service.repository import ServiceRepository
from app.domain.team.model import Team


def test_service_repository_crud_and_audit():
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        team = Team(name="platform", description="platform team")
        session.add(team)
        session.commit()

        repository = ServiceRepository(session)
        service = repository.create(
            Service(name="cmdb-api", team_id=team.id, description="cmdb api"),
            "request-create",
            "alice@example.com",
        )

        assert repository.get_by_id(service.id) is service
        assert repository.list() == [service]

        before = {
            "id": service.id,
            "name": service.name,
            "team_id": service.team_id,
            "description": service.description,
        }
        service.name = "cmdb"
        repository.update(service, before, "request-update", "bob@example.com")
        assert repository.get_by_id(service.id).name == "cmdb"

        service_id = service.id
        repository.delete(service, "request-delete", "carol@example.com")
        assert repository.get_by_id(service_id) is None

        changes = list(
            session.scalars(select(ChangeRecord).order_by(ChangeRecord.created_at)).all()
        )
        assert [change.action for change in changes] == ["create", "update", "delete"]
        assert changes[0].entity_id == service_id
        assert changes[1].before["name"] == "cmdb-api"
        assert changes[1].after["name"] == "cmdb"
        assert changes[2].before["id"] == service_id
        assert changes[2].after is None
