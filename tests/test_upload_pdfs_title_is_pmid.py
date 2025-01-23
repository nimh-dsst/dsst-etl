import unittest
from unittest.mock import MagicMock, patch
from dsst_etl.models import Documents, Identifier, OddpubMetrics, Works
from dsst_etl.upload_pdfs_title_is_pmid import UploadPDFsTitleIsPMID

from tests.base_test import BaseTest  # type: ignore


class TestUploadPDFsTitleIsPMID(BaseTest):

    @patch('dsst_etl.upload_pdfs_title_is_pmid.boto3.client')
    @patch('dsst_etl.upload_pdfs_title_is_pmid.get_bucket_name')
    def setUp(self, mock_get_bucket_name, mock_boto_client):
        super().setUp()

        # Mock S3 client and bucket name
        self.mock_s3_client = MagicMock()
        mock_boto_client.return_value = self.mock_s3_client
        mock_get_bucket_name.return_value = 'mock-bucket'

        # Initialize the class with the mocked session
        self.uploader = UploadPDFsTitleIsPMID(self.session)

    @patch('dsst_etl.upload_pdfs_title_is_pmid.logger')
    def test_process_s3_inventory_success(self, mock_logger):
        # Mock the S3 paginator and page iterator
        mock_page_iterator = [{'Contents': [{'Key': '12345678.pdf'}]}]
        self.uploader._get_s3_page_iterator = MagicMock(return_value=mock_page_iterator)

        # Mock existing hashes
        self.uploader._get_existing_hashes = MagicMock(return_value=set())

        # Mock provenance entry creation
        mock_provenance = MagicMock()
        self.uploader._create_provenance_entry = MagicMock(return_value=mock_provenance)

        # Mock S3 get_object response
        self.mock_s3_client.get_object.return_value = {'Body': MagicMock(read=MagicMock(return_value=b'pdf content'))}

        # Run the method
        self.uploader.process_s3_inventory('mock/path/to/pdf')

        # Assertions
        self.mock_db_session.commit.assert_called_once()
        mock_logger.info.assert_called_with("S3 inventory processing completed successfully")
        self.assertEqual(self.session.query(Documents).count(), 1)
        self.assertEqual(self.session.query(Identifier).count(), 1)
        self.assertEqual(self.session.query(Works).count(), 1)
        self.assertEqual(self.session.query(OddpubMetrics).count(), 1)

    @patch('dsst_etl.upload_pdfs_title_is_pmid.logger')
    def test_process_s3_inventory_failure(self, mock_logger):
        # Force an exception in the process
        self.uploader._get_s3_page_iterator = MagicMock(side_effect=Exception("Test exception"))

        # Run the method
        self.uploader.process_s3_inventory('mock/path/to/pdf')

        # Assertions
        self.mock_db_session.commit.assert_not_called()
        mock_logger.error.assert_called_with("Error processing S3 inventory: Test exception")
        self.assertEqual(self.session.query(Documents).count(), 0)
        self.assertEqual(self.session.query(Identifier).count(), 0)
        self.assertEqual(self.session.query(Works).count(), 0)
        self.assertEqual(self.session.query(OddpubMetrics).count(), 0)



if __name__ == '__main__':
    unittest.main()