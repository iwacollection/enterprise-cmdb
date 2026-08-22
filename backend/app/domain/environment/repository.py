from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.audit.model import ChangeRecord
from app.domain.environment.model import Environment


class EnvironmentRepository:
    def __init__(self, session: Session):
        self.session = session

    def list(self) -> list[Environment]:
        return list(self.session.scalars(select(Environment)).all())

    def get_by_id(self, environment_id: UUID) -> Environment | None:
        return self.session.get(Environment, environment_id)

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

    @staticmethod
    def _snapshot(environment: Environment) -> dict:
        return {
            "id": str(environment.id),
            "name": environment.name,
            "description": environment.description,
        }
