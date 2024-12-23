import logging
import unittest
from unittest.mock import patch, MagicMock
from sqlalchemy.orm import Session
from dsst_etl.oddpub_wrapper import OddpubWrapper
from dsst_etl.models import OddpubMetrics
from dsst_etl import get_db_engine
from dsst_etl.db import get_db_session, init_db
from sqlalchemy import inspect
logger = logging.getLogger(__name__)

class TestOddpubWrapper(unittest.TestCase):

    def setUp(self):
        # Mock the database session
        self.engine = get_db_engine(is_test=True)

        init_db(self.engine)
        # Create a new session for each test
        self.session = get_db_session(self.engine)

        self.wrapper = OddpubWrapper(
            db_session=self.session,
            oddpub_host_api="http://mock-api"
        )

    def tearDown(self):
        # # Rollback the transaction
        # self.session.rollback()

        # Check if the Works table exists before attempting to update or delete
        inspector = inspect(self.engine)
        tables = inspector.get_table_names()
        logger.info(f"Tables in the tearDown: {tables}")
        if "oddpub_metrics" in tables:
            self.session.query(OddpubMetrics).delete()
        self.session.commit()

    def test_oddpub_wrapper_without_mock_api(self):
        self.wrapper.oddpub_host_api = "http://localhost:8071"
        self.wrapper.process_pdfs("tests/pdf-test", force_upload=True)
        data = self.session.query(OddpubMetrics).all()
        self.assertEqual(len(data), 2)
        articles = [row.article for row in data]
        self.assertIn("test1.txt", articles)
        self.assertIn("test2.txt", articles)
        


    @patch("dsst_etl.oddpub_wrapper.requests.post")
    def test_process_pdfs_success(self, mock_post):
        # Mock the response from the API
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            'article': 'test1.txt', 
            'is_open_data': False, 
            'open_data_category': '', 
            'is_reuse': False, 
            'is_open_code': False, 
            'is_open_data_das': False, 
            'is_open_code_cas': False, 
            'das': None, 
            'open_data_statements': '', 
            'cas': None, 
            'open_code_statements': ''
        }
        
        mock_post.return_value = mock_response

        # Mock the PDF files
        pdf_folder = "tests/pdf-test"
        pdf_paths = [
            pdf_folder + "/test1.pdf",
        ]

        # Call the method
        self.wrapper.process_pdfs(pdf_folder, force_upload=True)

        # Assertions
        self.assertEqual(self.session.query(OddpubMetrics).count(), len(pdf_paths))

if __name__ == "__main__":
    unittest.main()
