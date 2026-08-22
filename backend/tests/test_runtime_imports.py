from app.database.base import Base
from app.database.engine import create_database_engine


def test_database_runtime_boundaries_import():
    assert Base is not None
    assert callable(create_database_engine)
