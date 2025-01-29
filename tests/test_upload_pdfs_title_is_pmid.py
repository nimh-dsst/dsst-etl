import unittest
from unittest.mock import MagicMock, patch
from dsst_etl.models import Documents, Identifier, OddpubMetrics, Works
from dsst_etl.upload_pdfs_title_is_pmid import DocumentInventoryPMID

from tests.base_test import BaseTest  # type: ignore


class TestDocumentInventoryPMID(BaseTest):

    @patch('dsst_etl.upload_pdfs_title_is_pmid.boto3.client')
    @patch('dsst_etl.upload_pdfs_title_is_pmid.get_bucket_name')
    def setUp(self, mock_get_bucket_name, mock_boto_client):
        super().setUp()

        # Mock S3 client and bucket name
        self.mock_s3_client = MagicMock()
        mock_boto_client.return_value = self.mock_s3_client
        mock_get_bucket_name.return_value = 'mock-bucket'

        # Initialize the class with the mocked session
        self.uploader = DocumentInventoryPMID(self.session, oddpub_host_api='http://mock-api:8071')

    @patch('requests.post')
    def test_process_s3_inventory_success(self, mock_post):
        # Mock the POST request
        def mock_post_side_effect(url, *args, **kwargs):
            if url == 'http://mock-api:8071/oddpub':
                mock_response = MagicMock()
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
                mock_response.status_code = 200
                return mock_response
            else:
                raise ValueError(f"Unexpected URL: {url}")

        mock_post.side_effect = mock_post_side_effect

        # Mock the S3 paginator and page iterator
        mock_page_iterator = [{'Contents': [{'Key': '12345678.pdf'}]}]
        self.uploader._get_s3_pdf_iterator = MagicMock(return_value=mock_page_iterator)

        # Mock S3 get_object response to return bytes
        self.mock_s3_client.get_object.return_value = {
            'Body': MagicMock(read=MagicMock(return_value=b'test content'))
        }

        # Run the method
        self.uploader.run()

        # Assertions
        self.assertEqual(self.session.query(Documents).count(), 1, "Documents table should have 1 row")
        self.assertEqual(self.session.query(Identifier).count(), 1, "Identifier table should have 1 row")
        self.assertEqual(self.session.query(Works).count(), 1, "Works table should have 1 row")
        self.assertEqual(self.session.query(OddpubMetrics).count(), 1, "OddpubMetrics table should have 1 row")

        # Check that the POST request was made to the correct URL
        mock_post.assert_called_with(
            'http://mock-api:8071/oddpub',
            files={'file': b'test content'}
        )

    @patch('dsst_etl.upload_pdfs_title_is_pmid.logger')
    def test_process_s3_inventory_failure(self, mock_logger):
        # Force an exception in the process
        self.uploader._get_s3_pdf_iterator = MagicMock(side_effect=Exception("Test exception"))

        # Run the method
        self.uploader.run()

        # Assertions
        mock_logger.error.assert_called_with("Error processing S3 inventory: Test exception")
        self.assertEqual(self.session.query(Documents).count(), 0)
        self.assertEqual(self.session.query(Identifier).count(), 0)
        self.assertEqual(self.session.query(Works).count(), 0)
        self.assertEqual(self.session.query(OddpubMetrics).count(), 0)


if __name__ == '__main__':
    unittest.main()