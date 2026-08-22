from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


DATABASE_URL = "sqlite+pysqlite:///:memory:"

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(bind=engine)
