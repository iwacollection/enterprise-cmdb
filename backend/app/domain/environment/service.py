from app.domain.environment.repository import EnvironmentRepository


class EnvironmentService:
    def __init__(self, repository: EnvironmentRepository):
        self.repository = repository

    def list_environments(self):
        return self.repository.list()
