from sqlalchemy import inspect
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import create_database, database_exists

from dsst_etl import logger

from .models import Base


def get_db_session(engine):
    Session = sessionmaker(bind=engine)
    return Session()


def init_db(engine):
    logger.info("Initializing database")

    if not database_exists(engine.url):
        logger.info("Creating database...")
        create_database(engine.url)
        logger.info("Database created")

    logger.info("Creating tables...")
    Base.metadata.create_all(engine)
    logger.info("Tables created successfully")

    # Log the list of tables
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    logger.info(f"Tables in the database: {tables}")
