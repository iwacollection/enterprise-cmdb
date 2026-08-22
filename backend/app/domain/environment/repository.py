from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.environment.model import Environment


class EnvironmentRepository:
    def __init__(self, session: Session):
        self.session = session

    def list(self) -> list[Environment]:
        return list(self.session.scalars(select(Environment)).all())

    def create(self, environment: Environment) -> Environment:
        self.session.add(environment)
        self.session.commit()
        self.session.refresh(environment)
        return environment
