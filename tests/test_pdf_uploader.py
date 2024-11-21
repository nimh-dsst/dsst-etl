import unittest
from unittest.mock import patch, MagicMock
from dsst_etl.upload_pdfs import PDFUploader
from dsst_etl.db import get_db_session
from dsst_etl.models import Documents, Provenance, Works
from pathlib import Path

class TestPDFUploader(unittest.TestCase):

    @patch('dsst_etl.upload_pdfs.boto3.client')
    def setUp(self, mock_boto_client):
        # Mock S3 client
        self.mock_s3_client = MagicMock()
        mock_boto_client.return_value = self.mock_s3_client

        # Start a new database session and transaction
        self.session = get_db_session()
        self.session.begin_nested()  # Start a nested transaction

        # Initialize PDFUploader with the session
        self.uploader = PDFUploader(self.session)

    def tearDown(self):
        # Rollback the transaction
        self.session.rollback()
        self.session.close()

    def test_upload_pdfs_success(self):
        # Mock successful upload
        self.mock_s3_client.upload_file.return_value = None

        base_dir = Path(__file__).resolve().parent
        pdf_paths = [base_dir / 'pdf-test' / 'test1.pdf', base_dir / 'pdf-test' / 'test2.pdf']
        successful_uploads, failed_uploads = self.uploader.upload_pdfs(pdf_paths)

        self.assertEqual(successful_uploads, pdf_paths)
        self.assertEqual(failed_uploads, [])
        self.mock_s3_client.upload_file.assert_called()

    def test_upload_pdfs_failure(self):
        # Mock failed upload
        self.mock_s3_client.upload_file.side_effect = Exception("Upload failed")

        base_dir = Path(__file__).resolve().parent
        pdf_paths = [base_dir / 'pdf-test' / 'test1.pdf', base_dir / 'pdf-test' / 'test2.pdf']
        successful_uploads, failed_uploads = self.uploader.upload_pdfs(pdf_paths)

        self.assertEqual(successful_uploads, [])
        self.assertEqual(failed_uploads, pdf_paths)

    def test_create_document_records(self):
        base_dir = Path(__file__).resolve().parent
        successful_uploads = [base_dir / 'pdf-test' / 'test1.pdf']
        print(successful_uploads)
        documents = self.uploader.create_document_records(successful_uploads)

        self.assertEqual(len(documents), 1)
        self.assertEqual(self.session.query(Documents).count(), 1)

    def test_create_provenance_record(self):
        documents = [self.session.query(Documents).first()]
        self.session.add_all(documents)
        self.session.commit()

        provenance = self.uploader.create_provenance_record(documents, "Test comment")

        self.assertIsInstance(provenance, Provenance)
        self.assertEqual(self.session.query(Provenance).count(), 1)

    def test_initial_work_for_document(self):
        document = self.session.query(Documents).first()
        provenance = Provenance(pipeline_name="test", version="0.0.1", compute="test", personnel="test", comment="test")
        self.session.add_all([document, provenance])
        self.session.commit()

        work = self.uploader.initial_work_for_document(document, provenance)

        self.assertIsInstance(work, Works)
        self.assertEqual(self.session.query(Works).count(), 1)

    def test_link_documents_to_work(self):
        documents = self.session.query(Documents).all()
        work_id = 1
        self.uploader.link_documents_to_work([doc.id for doc in documents], work_id)

        # Assuming link_documents_to_work modifies the documents in some way
        # Add assertions here to verify the expected changes
        self.assertEqual(self.session.query(Documents).count(), len(documents))
        # Check that the documents have the correct work_id
        for doc in documents:
            self.assertEqual(doc.work_id, work_id)

if __name__ == '__main__':
    unittest.main()