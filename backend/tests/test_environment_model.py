from app.domain.environment.model import Environment


def test_environment_model_definition():
    assert Environment.__tablename__ == "environments"
