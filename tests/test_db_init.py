from dsst_etl import get_db_engine
from dsst_etl.db import init_db


def test_init_db():
    engine = get_db_engine(is_test=True)
    init_db(engine)
