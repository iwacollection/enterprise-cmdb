from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.database.base import Base
from app.domain.audit.model import ChangeRecord
from app.domain.environment.model import Environment
from app.domain.environment.repository import EnvironmentRepository


def test_environment_repository_persistence_and_audit():
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        repository = EnvironmentRepository(session)
        environment = repository.create(
            Environment(name="production", description="prod"),
            "request-create",
            "alice@example.com",
        )

        before = {
            "id": str(environment.id),
            "name": environment.name,
            "description": environment.description,
        }
        environment.description = "primary production"
        repository.update(environment, before, "request-update", "bob@example.com")

        environment_id = environment.id
        repository.delete(environment, "request-delete", "carol@example.com")
        assert repository.get_by_id(environment_id) is None

        changes = list(
            session.scalars(select(ChangeRecord).order_by(ChangeRecord.created_at)).all()
        )
        assert [change.action for change in changes] == ["create", "update", "delete"]
        assert changes[0].entity_type == "environment"
        assert changes[0].changed_by == "alice@example.com"
        assert changes[1].before["description"] == "prod"
        assert changes[1].after["description"] == "primary production"
        assert changes[2].before["id"] == str(environment_id)
        assert changes[2].after is None
