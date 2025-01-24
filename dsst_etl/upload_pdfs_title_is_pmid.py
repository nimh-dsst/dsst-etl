import hashlib

import boto3
import requests
import sqlalchemy
from sqlalchemy.exc import SQLAlchemyError

from dsst_etl import __version__, logger
from dsst_etl._utils import get_bucket_name, get_compute_context_id
from dsst_etl.models import Documents, Identifier, OddpubMetrics, Provenance, Works

from .config import config


class UploadPDFsTitleIsPMID:
    """
    Uploads PDFs to S3 where the title is the PMID.
    """

    def __init__(
        self,
        db_session: sqlalchemy.orm.Session,
        oddpub_host_api: str = config.ODDPUB_HOST_API,
    ):
        self.db_session = db_session
        self.bucket_name = get_bucket_name()
        self.s3_client = boto3.client("s3")
        self.oddpub_host_api = oddpub_host_api

    def run(self) -> str:
        """
        Executes the process of reading PDFs in S3 bucket where the title of pdf files is the PMID.

        This method performs the following steps:
        1. Retrieves an iterator for paginated S3 objects.
        2. Creates a provenance entry for the current upload process.
        3. Iterates over each page of S3 objects, processing each PDF file:
        - Skips non-PDF files.
        - Computes the hash of the PDF content.
        - Creates document, work, and identifier entries in the database.
        - Runs Oddpub analysis on the PDF content.
        4. Commits the database session upon successful processing.
        5. Logs the completion of the process or any errors encountered.
        """
        try:
            pdf_iterator = self._get_s3_pdf_iterator()
            provenance = self._create_provenance_entry()

            for pdf_batch in pdf_iterator:
                self._process_pdf_batch(pdf_batch, provenance)
            self.db_session.commit()
            logger.info("S3 inventory processing completed successfully")

        except Exception as e:
            logger.error(f"Error processing S3 inventory: {str(e)}")

    def _get_s3_pdf_iterator(self):
        # Retrieves a paginator for S3 objects, allowing iteration over batches of objects
        paginator = self.s3_client.get_paginator("list_objects_v2")
        return paginator.paginate(Bucket=self.bucket_name)

    def _create_provenance_entry(self):
        # Creates a provenance entry to track the current upload process
        provenance = Provenance(
            pipeline_name="Document Upload",
            version=__version__,
            compute=get_compute_context_id(),
            personnel=config.HOSTNAME,
            comment="Upload PDFs where the title is the PMID",
        )
        self.db_session.add(provenance)
        self.db_session.commit()
        return provenance

    def _process_pdf_batch(self, pdf_batch, provenance):
        # Processes each PDF file in the current batch
        for obj in pdf_batch.get("Contents", []):
            key = obj["Key"]
            if not key.endswith(".pdf"):
                continue
            logger.info(f"processing key: {key}")

            response = self.s3_client.get_object(Bucket=self.bucket_name, Key=key)
            file_content = response["Body"].read()

            try:
                file_hash = hashlib.sha256(file_content).hexdigest()
            except Exception as e:
                logger.error(f"Error hashing file: {str(e)}")
                continue

            # Use a transaction context manager to ensure atomicity
            try:
                with self.db_session.begin_nested():
                    self._create_document_entries(
                        key, file_content, file_hash, provenance
                    )
            except SQLAlchemyError as e:
                logger.error(f"Transaction failed for document {key}: {str(e)}")
                self.db_session.rollback()

    def _create_document_entries(self, key, file_content, file_hash, provenance):
        # Creates database entries for the document, work, and identifier
        try:
            document = Documents(
                hash_data=file_hash,
                s3uri=f"s3://{self.bucket_name}/{key}",
                provenance_id=provenance.id,
            )
            self.db_session.add(document)
            self.db_session.flush()

            work = Works(
                initial_document_id=document.id,
                primary_document_id=document.id,
                provenance_id=provenance.id,
            )
            self.db_session.add(work)
            self.db_session.flush()

            identifier = Identifier(
                pmid=key.split("/")[-1].split(".")[0],
                document_id=document.id,
                provenance_id=provenance.id,
            )
            self.db_session.add(identifier)
            self.db_session.flush()
        except SQLAlchemyError as e:
            logger.error(f"Error creating document entries: {str(e)}")
            raise  # Re-raise to trigger rollback

        # Run Oddpub analysis
        try:
            response = requests.post(
                f"{self.oddpub_host_api}/oddpub", files={"file": file_content}
            )
            response.raise_for_status()
            r_result = response.json()
            oddpub_metrics = OddpubMetrics(**r_result)
            oddpub_metrics.work_id = work.id
            oddpub_metrics.document_id = document.id
            oddpub_metrics.provenance_id = provenance.id
            self.db_session.add(oddpub_metrics)
            self.db_session.commit()
        except Exception as e:
            logger.error(f"Error running Oddpub analysis: {str(e)}")
            raise  # Re-raise to trigger rollback
