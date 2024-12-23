import unittest
from dsst_etl import get_db_engine
from dsst_etl.db import get_db_session_new, init_db

class BaseTest(unittest.TestCase):

    def setUp(self):
        self.engine = get_db_engine(is_test=True)
        init_db(self.engine)

        # Start a transaction at the connection level
        self.connection = self.engine.connect()
        self.trans = self.connection.begin()
        
        # Create session bound to this connection
        self.session = get_db_session_new(bind=self.connection)

    def tearDown(self):
        if self.session.is_active:
            self.session.close()
        
        # Roll back the transaction
        if self.trans.is_active:
            self.trans.rollback()
        
        # Close the connection
        self.connection.close() 