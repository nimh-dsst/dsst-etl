import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from dsst_etl.models import Documents, Identifier, Provenance, Works
from dsst_etl.upload_pdfs import PDFUploader
from tests.base_test import BaseTest  # type: ignore


class TestPDFUploader(BaseTest):

    @patch("dsst_etl.upload_pdfs.boto3.client")
    def setUp(self, mock_boto_client):
        super().setUp()
        self.mock_s3_client = MagicMock()
        mock_boto_client.return_value = self.mock_s3_client
        self.uploader = PDFUploader(self.session)
        self.base_dir = Path(__file__).resolve().parent
        self.pdf_paths = f"{self.base_dir}/pdf-test"
        self.metadata_json_file_path = f"{self.base_dir}/pdf-test/metadata.json"

    def test_run_uploader_successful_uploads(self):
        """Test that the uploader runs and uploads files successfully."""
        self.mock_s3_client.upload_file.return_value = None

        successful_uploads, failed_uploads = self.uploader.run_uploader(
            pdf_directory_path=self.pdf_paths,
            metadata_json_file_path=self.metadata_json_file_path,
            comment="Test upload comment",
        )

        self.assertEqual(len(successful_uploads), 2)
        self.assertEqual(len(failed_uploads), 0)
        self.mock_s3_client.upload_file.assert_called()

    def test_identifiers_created(self):
        """Test that identifiers are created correctly."""
        self.test_run_uploader_successful_uploads()

        identifiers = self.session.query(Identifier).all()
        self.assertEqual(len(identifiers), 2)
        self.assertIn("10.1038/s41586-023-06521-1", [identifier.doi for identifier in identifiers])
        self.assertIn("10.1038/s41586-023-06521-2", [identifier.doi for identifier in identifiers])
        self.assertIn(34567890, [identifier.pmid for identifier in identifiers])
        self.assertIn(45678901, [identifier.pmid for identifier in identifiers])
        self.assertIn("PMC9876543", [identifier.pmcid for identifier in identifiers])
        self.assertIn("PMC1234567", [identifier.pmcid for identifier in identifiers])

    def test_documents_created(self):
        """Test that documents are created correctly."""
        self.test_run_uploader_successful_uploads()

        documents = self.session.query(Documents).all()
        self.assertEqual(len(documents), 2)
        self.assertIn("s3://osm-pdf-uploads/pdfs/test2.pdf", [document.s3uri for document in documents])
        self.assertIn("s3://osm-pdf-uploads/pdfs/test1.pdf", [document.s3uri for document in documents])

    def test_provenance_created(self):
        """Test that provenance is created correctly."""
        self.test_run_uploader_successful_uploads()

        provenance = self.session.query(Provenance).first()
        self.assertEqual(provenance.comment, "Test upload comment")
        self.assertEqual(provenance.pipeline_name, "Document Upload")

    def test_documents_linked_to_provenance(self):
        """Test that documents are linked to the correct provenance."""
        self.test_run_uploader_successful_uploads()

        documents = self.session.query(Documents).all()
        provenance = self.session.query(Provenance).first()
        self.assertEqual(documents[0].provenance_id, provenance.id)
        self.assertEqual(documents[1].provenance_id, provenance.id)

    def test_works_created(self):
        """Test that works are created correctly."""
        self.test_run_uploader_successful_uploads()

        works = self.session.query(Works).all()
        documents = self.session.query(Documents).all()
        self.assertEqual(len(works), 2)
        self.assertIn(works[0].initial_document_id, [document.id for document in documents])

    def test_empty_pdf_directory(self):
        """Test that the uploader handles an empty PDF directory gracefully."""
        self.mock_s3_client.upload_file.return_value = None

        empty_pdf_dir = f"{self.base_dir}/empty-pdf-test"
        successful_uploads, failed_uploads = self.uploader.run_uploader(
            pdf_directory_path=empty_pdf_dir,
            metadata_json_file_path=self.metadata_json_file_path,
            comment="Test upload comment",
        )

        self.assertEqual(len(successful_uploads), 0)
        self.assertEqual(len(failed_uploads), 0)

    def test_invalid_metadata_json(self):
        """Test that the uploader handles invalid metadata JSON files."""
        self.mock_s3_client.upload_file.return_value = None

        invalid_metadata_json_file_path = f"{self.base_dir}/pdf-test/invalid_metadata.json"
        with self.assertRaises(FileNotFoundError):
            self.uploader.run_uploader(
                pdf_directory_path=self.pdf_paths,
                metadata_json_file_path=invalid_metadata_json_file_path,
                comment="Test upload comment",
            )

    def test_partial_upload_failures(self):
        """Test that the uploader correctly reports partial upload failures."""
        def mock_upload_file(Bucket, Key, Filename):
            if "test1.pdf" in Filename:
                raise Exception("Upload failed for test1.pdf")
            return None

        self.mock_s3_client.upload_file.side_effect = mock_upload_file

        successful_uploads, failed_uploads = self.uploader.run_uploader(
            pdf_directory_path=self.pdf_paths,
            metadata_json_file_path=self.metadata_json_file_path,
            comment="Test upload comment",
        )

        self.assertEqual(len(successful_uploads), 1)
        self.assertEqual(len(failed_uploads), 1)


if __name__ == "__main__":
    unittest.main()