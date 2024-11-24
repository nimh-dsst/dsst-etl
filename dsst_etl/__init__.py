"""
DSST ETL Package
"""

import logging
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .config import config

logger = logging.getLogger(__name__)


def get_db_url():
    database_url = (
        "postgresql://"
        f"{config.POSTGRES_USER}"
        f":{config.POSTGRES_PASSWORD}"
        f"@{config.POSTGRES_HOST}:"
        f"{config.POSTGRES_PORT}/{config.POSTGRES_DB}"
    )
    return database_url


def get_db_url_test():
    database_url = (
        "postgresql://"
        f"{config.POSTGRES_USER}"
        f":{config.POSTGRES_PASSWORD}"
        f"@{config.POSTGRES_HOST}:"
        f"{config.POSTGRES_PORT}/{config.POSTGRES_DB_UNIT_TEST}"
    )
    return database_url


def get_db_engine(is_test=False):
    if is_test:
        return create_engine(get_db_url_test())
    else:
        return create_engine(get_db_url())


engine = get_db_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_version():
    try:
        from . import _version

        return _version.version
    except ImportError:
        generate_version_file()
        from . import _version

        return _version.version


def generate_version_file():
    import pkg_resources

    version = pkg_resources.get_distribution("dsst_etl").version
    version_file_content = f"version = '{version}'\n"

    version_file_path = os.path.join(os.path.dirname(__file__), "_version.py")
    with open(version_file_path, "w") as version_file:
        version_file.write(version_file_content)


__version__ = get_version()
