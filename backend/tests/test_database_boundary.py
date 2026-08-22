def test_database_boundary_module_import():
    from app.database.base import Base

    assert Base is not None
