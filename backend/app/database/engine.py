"""Database engine boundary.

Connection creation is intentionally isolated from domain code.
"""

from sqlalchemy import create_engine


# Placeholder until runtime database configuration is finalized.
# No connection is created during module import.


def create_database_engine(database_url: str):
    return create_engine(database_url)
