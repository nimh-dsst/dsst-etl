from sqlalchemy import inspect
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy_utils import database_exists

from dsst_etl import logger


def get_db_session(engine):
    Session = sessionmaker(bind=engine)
    return Session()


def get_db_session_new(engine=None, bind=None):
    if bind:
        return Session(bind=bind)
    return Session(engine)


def init_db(engine):
    logger.info("Checking database initialization")

    if not database_exists(engine.url):
        raise RuntimeError(
            "Database does not exist. Please create it and run Alembic migrations."
        )

    # Check if tables exist
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    if not tables:
        raise RuntimeError(
            "Database schema is not initialized. Please run Alembic migrations."
        )

    logger.info(f"Tables in the database: {tables}")
