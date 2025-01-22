import unittest
from unittest.mock import MagicMock, patch

from dsst_etl.models import OddpubMetrics
from dsst_etl.oddpub_wrapper import OddpubWrapper


class TestOddpubWrapper(unittest.TestCase):

    @patch('dsst_etl.oddpub_wrapper.requests.post')
    @patch('dsst_etl.oddpub_wrapper.Path.glob')
    def test_process_pdfs(self, mock_glob, mock_post):
        # Setup
        mock_session = MagicMock()
        mock_glob.return_value = [MagicMock(name='file1.pdf'), MagicMock(name='file2.pdf')]
        mock_post.return_value.json.return_value = {'metric1': 'value1', 'metric2': 'value2'}
        mock_post.return_value.raise_for_status = MagicMock()

        wrapper = OddpubWrapper(db_session=mock_session, work_id=1, document_id=1)

        # Execute
        result = wrapper.process_pdfs(pdf_folder='/fake/path', force_upload=True)

        # Verify
        self.assertIsInstance(result, OddpubMetrics)
        self.assertEqual(result.metric1, 'value1')
        self.assertEqual(result.metric2, 'value2')
        self.assertEqual(mock_session.add.call_count, 2)
        mock_session.commit.assert_called_once()

    @patch('dsst_etl.oddpub_wrapper.boto3.client')
    @patch('dsst_etl.oddpub_wrapper.hashlib.sha256')
    def test_process_s3_inventory(self, mock_sha256, mock_boto3_client):
        # Setup
        mock_session = MagicMock()
        mock_s3_client = MagicMock()
        mock_boto3_client.return_value = mock_s3_client
        mock_sha256.return_value.hexdigest.return_value = 'fakehash'

        mock_s3_client.get_paginator.return_value.paginate.return_value = [
            {'Contents': [{'Key': 'file1.pdf'}, {'Key': 'file2.pdf'}]}
        ]
        mock_s3_client.get_object.return_value['Body'].read.return_value = b'fakecontent'

        wrapper = OddpubWrapper(db_session=mock_session)

        # Execute
        wrapper.process_s3_inventory(s3_bucket='fake-bucket', inventory_prefix='fake-prefix')

        # Verify
        self.assertEqual(mock_session.add.call_count, 6)  # 2 documents, 2 works, 2 provenances
        self.assertEqual(mock_session.commit.call_count, 6)
        mock_s3_client.get_paginator.assert_called_once_with('list_objects_v2')
        mock_s3_client.get_object.assert_called()

if __name__ == '__main__':
    unittest.main()
