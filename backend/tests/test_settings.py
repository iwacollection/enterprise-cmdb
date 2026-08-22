import os

import pytest

from app.config.settings import _database_url


def test_database_url_prefers_explicit_url(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "sqlite+pysqlite:///explicit.db")

    assert _database_url() == "sqlite+pysqlite:///explicit.db"


def test_database_url_builds_postgres_url_and_escapes_credentials(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setenv("CMDB_DB_HOST", "cmdb.postgres.database.azure.com")
    monkeypatch.setenv("CMDB_DB_USER", "cmdb_admin")
    monkeypatch.setenv("CMDB_DB_PASSWORD", "p@ss:/#word")
    monkeypatch.setenv("CMDB_DB_NAME", "cmdb")

    assert _database_url() == (
        "postgresql+psycopg://cmdb_admin:p%40ss%3A%2F%23word@"
        "cmdb.postgres.database.azure.com:5432/cmdb?sslmode=require"
    )


def test_component_database_config_fails_fast_when_required_value_missing(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setenv("CMDB_DB_HOST", "cmdb.postgres.database.azure.com")
    monkeypatch.setenv("CMDB_DB_USER", "cmdb_admin")
    monkeypatch.delenv("CMDB_DB_PASSWORD", raising=False)
    monkeypatch.setenv("CMDB_DB_NAME", "cmdb")

    with pytest.raises(KeyError, match="CMDB_DB_PASSWORD"):
        _database_url()

    monkeypatch.delenv("CMDB_DB_HOST", raising=False)
    for key in ("CMDB_DB_USER", "CMDB_DB_NAME"):
        os.environ.pop(key, None)
