import logging
import unittest
from dsst_etl.oddpub_wrapper import OddpubWrapper
from dsst_etl.models import OddpubMetrics

from tests.base_test import BaseTest # type: ignore
logger = logging.getLogger(__name__)

class TestOddpubWrapper(BaseTest):

    def setUp(self):
        super().setUp()

        self.wrapper = OddpubWrapper(
            db_session=self.session,
            oddpub_host_api="http://mock-api"
        )

    def test_oddpub_wrapper_without_mock_api(self):
        self.wrapper.oddpub_host_api = "http://localhost:8071"
        self.wrapper.process_pdfs("tests/pdf-test", force_upload=True)
        data = self.session.query(OddpubMetrics).all()
        self.assertEqual(len(data), 2)
        articles = [row.article for row in data]
        self.assertIn("test1.txt", articles)
        self.assertIn("test2.txt", articles)
        

if __name__ == "__main__":
    unittest.main()
