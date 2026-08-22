from app.domain.environment.model import Environment
from app.domain.environment.repository import EnvironmentRepository
from app.domain.environment.schema import EnvironmentCreate


class EnvironmentService:
    def __init__(self, repository: EnvironmentRepository):
        self.repository = repository

    def list_environments(self):
        return self.repository.list()

    def create_environment(self, data: EnvironmentCreate):
        environment = Environment(
            name=data.name,
            description=data.description,
        )
        return self.repository.create(environment)
