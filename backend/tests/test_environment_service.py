from app.domain.environment.schema import EnvironmentCreate


class FakeRepository:
    def __init__(self):
        self.created = None
        self.audit = None

    def create(self, environment, request_id, changed_by):
        self.created = environment
        self.audit = (request_id, changed_by)
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
        EnvironmentCreate(name="production", description="prod"),
        "request-1",
        "alice@example.com",
    )

    assert result.name == "production"
    assert repository.created is result
    assert repository.audit == ("request-1", "alice@example.com")
