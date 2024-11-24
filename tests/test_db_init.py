from dsst_etl.db import init_db


def test_init_db():
    init_db(is_test=True)
