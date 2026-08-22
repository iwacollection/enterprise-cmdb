from uuid import UUID

from app.domain.environment.model import Environment
from app.domain.environment.repository import EnvironmentRepository
from app.domain.environment.schema import EnvironmentCreate, EnvironmentUpdate


class EnvironmentService:
    def __init__(self, repository: EnvironmentRepository):
        self.repository = repository

    def list_environments(self) -> list[Environment]:
        return self.repository.list()

    def get_environment(self, environment_id: UUID) -> Environment | None:
        return self.repository.get_by_id(environment_id)

    def create_environment(self, data: EnvironmentCreate) -> Environment:
        environment = Environment(
            name=data.name,
            description=data.description,
        )
        return self.repository.create(environment)

    def update_environment(
        self,
        environment: Environment,
        data: EnvironmentUpdate,
    ) -> Environment:
        environment.name = data.name
        environment.description = data.description
        return self.repository.update(environment)
