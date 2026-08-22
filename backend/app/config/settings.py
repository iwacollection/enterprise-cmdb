import os
from dataclasses import dataclass
from urllib.parse import quote_plus


def _database_url() -> str:
    explicit_url = os.environ.get("DATABASE_URL")
    if explicit_url:
        return explicit_url

    host = os.environ.get("CMDB_DB_HOST")
    if host is None:
        return "sqlite+pysqlite:///./cmdb.db"

    user = os.environ["CMDB_DB_USER"]
    password = os.environ["CMDB_DB_PASSWORD"]
    database = os.environ["CMDB_DB_NAME"]
    port = os.environ.get("CMDB_DB_PORT", "5432")

    return (
        "postgresql+psycopg://"
        f"{quote_plus(user)}:{quote_plus(password)}@{host}:{port}/{quote_plus(database)}"
        "?sslmode=require"
    )


def _auth_mode() -> str:
    value = os.environ.get("CMDB_AUTH_MODE", "local")
    if value not in {"local", "entra"}:
        raise ValueError("CMDB_AUTH_MODE must be 'local' or 'entra'")
    return value


@dataclass(frozen=True)
class Settings:
    app_name: str = "enterprise-cmdb"
    database_url: str = _database_url()
    auth_mode: str = _auth_mode()


settings = Settings()
