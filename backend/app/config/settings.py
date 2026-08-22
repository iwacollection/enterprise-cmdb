import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    app_name: str = "enterprise-cmdb"
    database_url: str = os.environ.get(
        "DATABASE_URL",
        "sqlite+pysqlite:///./cmdb.db",
    )


settings = Settings()
