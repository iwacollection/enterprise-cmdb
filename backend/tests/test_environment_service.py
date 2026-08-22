from app.domain.environment.schema import EnvironmentCreate


class FakeRepository:
    def __init__(self):
        self.created = None

    def create(self, environment):
        self.created = environment
        return environment

    def list(self):
        return []

    def get_by_id(self, environment_id):
        return None


def test_create_environment_service():
    from app.domain.environment.service import EnvironmentService

    repository = FakeRepository()
    service = EnvironmentService(repository)

    result = service.create_environment(
        EnvironmentCreate(name="production", description="prod")
    )

    assert result.name == "production"
    assert repository.created is result
