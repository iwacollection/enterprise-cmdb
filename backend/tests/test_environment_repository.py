from app.domain.environment.model import Environment


def test_environment_repository_contract():
    assert Environment.__tablename__ == "environments"
