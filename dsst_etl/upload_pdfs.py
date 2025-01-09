import argparse
import hashlib
import json
import os
from pathlib import Path
from typing import List, Optional, Tuple

import boto3
import sqlalchemy

from dsst_etl import __version__, get_db_engine, logger
from dsst_etl._utils import (
    convert_metadata_to_identifier,
    get_bucket_name,
    get_compute_context_id,
)
from dsst_etl.models import Documents, Identifier, Provenance, Works

from .config import config


class PDFUploader:
    """
    Handles PDF uploads to S3 and maintains database records of uploads.

    This class manages:
    1. Uploading PDFs to S3
    2. Creating document records
    3. Maintaining provenance logs
    4. Linking documents to works
    """

    def __init__(self, db_session: sqlalchemy.orm.Session):
        """
        Initialize the uploader with S3 bucket and database connection.

        Args:
            bucket_name (str): Name of the S3 bucket for PDF storage
        """
        self.bucket_name = get_bucket_name()
        self.s3_client = boto3.client("s3")
        self.db_session = db_session

    def __upload_pdf_file_to_s3(self, pdf_path: str) -> bool:
        """
        Upload a single PDF file to S3.

        Args:
            pdf_path (str): Path to the PDF file

        Returns:
            string: S3 URI of the uploaded file
        """
        try:
            s3_key = f"pdfs/{os.path.basename(pdf_path)}"
            self.s3_client.upload_file(pdf_path, self.bucket_name, s3_key)
            return s3_key
        except Exception as e:
            logger.error(f"Failed to upload {pdf_path}: {e}")
            return None

    def __create_provenance_record(self, comment: str = None) -> Provenance:
        """
        Create a provenance record for the upload batch and link it to documents.

        Args:
            comment (str): Comment about the upload batch

        Returns:
            Provenance: Created provenance record
        """
        provenance = Provenance(
            pipeline_name="Document Upload",
            version=__version__,
            compute=get_compute_context_id(),
            personnel=config.HOSTNAME,
            comment=comment,
        )

        self.db_session.add(provenance)
        self.db_session.flush()

        self.db_session.commit()
        logger.info(f"Created provenance record {provenance.id}")
        return provenance

    def __upload_pdfs_with_metadata(
        self,
        pdf_paths: List[str],
        metadata: dict,
        is_pmids: bool = False,
        provenance_comment: str = None,
    ) -> Tuple[List[str], List[str]]:
        """
        Upload PDFs to S3 and create identifier records based on metadata.

        Args:
            pdf_paths (List[str]): List of paths to PDF files
            metadata (dict): Metadata for each PDF file

        Returns:
            Tuple[List[str], List[str]]: Lists of successful and failed uploads
        """
        transformed_metadata = convert_metadata_to_identifier(metadata)
        provenance = self.__create_provenance_record(provenance_comment)
        failed_uploads = []
        susccessful_uploads = []

        for pdf_path in pdf_paths:
            # Upload the file to S3
            doc_uri = self.__upload_pdf_file_to_s3(pdf_path)
            if not doc_uri:
                failed_uploads.append(pdf_path)
                continue

            pdf_path = Path(pdf_path)
            file_content = pdf_path.read_bytes()
            hash_data = hashlib.md5(file_content).hexdigest()

            document = Documents(
                hash_data=hash_data,
                s3uri=f"s3://{self.bucket_name}/{doc_uri}",
                provenance_id=provenance.id,
            )

            # Add the document to the session and flush to get the ID
            self.db_session.add(document)
            self.db_session.flush()

            # Add work for document
            work = Works(
                initial_document_id=document.id,
                primary_document_id=document.id,
                provenance_id=provenance.id,
            )
            self.db_session.add(work)

            file_metadata = transformed_metadata.get(pdf_path.name, {})
            if file_metadata or is_pmids:
                identifier = Identifier(
                    document_id=document.id,
                    provenance_id=provenance.id,
                    pmid=file_metadata.get("PMID"),
                    doi=file_metadata.get("DOI"),
                    pmcid=file_metadata.get("PMCID"),
                )
                self.db_session.add(identifier)

            self.db_session.commit()

            susccessful_uploads.append(pdf_path)

        return susccessful_uploads, failed_uploads

    def run_uploader(
        self,
        pdf_directory_path: str,
        metadata_json_file_path: Optional[str],
        is_pmids: Optional[bool] = False,
        comment: Optional[str] = None,
    ) -> Tuple[List[str], List[str]]:
        """
        Upload PDFs to S3 and create document records in the database.

        Args:
            pdf_paths (List[str]): List of paths to PDF files
            metadata (dict): Metadata for each PDF file

        Returns:
            Tuple[List[str], List[str]]: Lists of successful and failed uploads
        """
        pdf_directory = Path(pdf_directory_path)
        pdf_files = list(pdf_directory.glob("*.pdf"))

        if not pdf_files:
            logger.warning(f"No PDF files found in {pdf_directory_path}")
            return [], []

        with open(metadata_json_file_path) as f:
            metadata = json.load(f)

        return self.__upload_pdfs_with_metadata(pdf_files, metadata, is_pmids, comment)


def main():
    parser = argparse.ArgumentParser(
        description="Upload PDFs to S3 and create document records in the database."
    )
    parser.add_argument(
        "pdf_directory_path",
        type=str,
        help="Path to the directory containing PDF files",
    )
    parser.add_argument(
        "metadata_json_file_path",
        type=str,
        help="Path to the JSON file containing metadata",
    )
    parser.add_argument(
        "--is_pmids", action="store_true", help="Flag to indicate if PMIDs are used"
    )
    parser.add_argument(
        "--comment", type=str, help="Comment about the upload batch", default=None
    )

    args = parser.parse_args()

    # Initialize PDFUploader with appropriate db_session and bucket_name
    uploader = PDFUploader(get_db_engine())
    successful_uploads, failed_uploads = uploader.run_uploader(
        args.pdf_directory_path,
        args.metadata_json_file_path,
        args.is_pmids,
        args.comment,
    )

    logger.info("Successful uploads: %s", successful_uploads)
    logger.info("Failed uploads: %s", failed_uploads)


if __name__ == "__main__":
    main()
