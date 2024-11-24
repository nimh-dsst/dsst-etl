import logging

from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import create_database, database_exists

from dsst_etl import get_db_engine

from .models import Base

logger = logging.getLogger(__name__)


def get_db_session(is_test=False):
    engine = get_db_engine(is_test)
    Session = sessionmaker(bind=engine)
    return Session()


def init_db(is_test=False):
    engine = get_db_engine(is_test)

    if not database_exists(engine.url):
        logger.info("Creating database.....")
        create_database(engine.url)
    Base.metadata.create_all(engine)
