from app.domain.environment.schema import EnvironmentCreate


def test_environment_create_schema():
    item = EnvironmentCreate(name="production")
    assert item.name == "production"
