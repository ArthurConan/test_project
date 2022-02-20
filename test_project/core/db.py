from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from test_project.core.settings import get_settings


pg_host = get_settings().postgresql.host
pg_port = get_settings().postgresql.port
pg_user = get_settings().postgresql.user
pg_password = get_settings().postgresql.password
pg_db = get_settings().postgresql.db
pg_db_url = f"postgresql+psycopg2://{pg_user}:{pg_password}@{pg_host}:{pg_port}/{pg_db}"

engine = create_engine(pg_db_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Session:
    with SessionLocal() as session:
        yield session
