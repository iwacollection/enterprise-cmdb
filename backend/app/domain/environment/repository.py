from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.asset.model import Asset
from app.domain.audit.model import ChangeRecord
from app.domain.environment.model import Environment


class EnvironmentRepository:
    def __init__(self, session: Session):
        self.session = session

    def list(self) -> list[Environment]:
        return list(self.session.scalars(select(Environment)).all())

    def get_by_id(self, environment_id: UUID) -> Environment | None:
        return self.session.get(Environment, environment_id)

    def name_in_use(self, name: str, exclude_id: UUID | None = None) -> bool:
        statement = select(Environment.id).where(Environment.name == name)
        if exclude_id is not None:
            statement = statement.where(Environment.id != exclude_id)
        return self.session.scalar(statement.limit(1)) is not None

    def is_referenced(self, environment_id: UUID) -> bool:
        statement = select(Asset.id).where(Asset.environment_id == environment_id).limit(1)
        return self.session.scalar(statement) is not None

    def create(self, environment: Environment, request_id: str, changed_by: str) -> Environment:
        self.session.add(environment)
        self.session.flush()
        self.session.add(
            ChangeRecord(
                request_id=request_id,
                entity_type="environment",
                entity_id=str(environment.id),
                action="create",
                changed_by=changed_by,
                before=None,
                after=self._snapshot(environment),
            )
        )
        self.session.commit()
        self.session.refresh(environment)
        return environment

    def update(
        self,
        environment: Environment,
        before: dict,
        request_id: str,
        changed_by: str,
    ) -> Environment:
        self.session.add(
            ChangeRecord(
                request_id=request_id,
                entity_type="environment",
                entity_id=str(environment.id),
                action="update",
                changed_by=changed_by,
                before=before,
                after=self._snapshot(environment),
            )
        )
        self.session.commit()
        self.session.refresh(environment)
        return environment

    def delete(self, environment: Environment, request_id: str, changed_by: str) -> None:
        before = self._snapshot(environment)
        self.session.delete(environment)
        self.session.add(
            ChangeRecord(
                request_id=request_id,
                entity_type="environment",
                entity_id=str(environment.id),
                action="delete",
                changed_by=changed_by,
                before=before,
                after=None,
            )
        )
        self.session.commit()

    @staticmethod
    def _snapshot(environment: Environment) -> dict:
        return {
            "id": str(environment.id),
            "name": environment.name,
            "description": environment.description,
        }
