from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    app_name: str = "enterprise-cmdb"
    database_url: str = "sqlite+pysqlite:///:memory:"


settings = Settings()
