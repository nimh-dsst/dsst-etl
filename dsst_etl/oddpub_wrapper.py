import hashlib
import logging
from pathlib import Path

import boto3
import requests
from sqlalchemy.orm import Session

from dsst_etl.models import Documents, OddpubMetrics, Provenance, Works

from .config import config

logger = logging.getLogger(__name__)


class OddpubWrapper:
    """
    Wrapper class for the ODDPub API.
    """

    def __init__(
        self,
        db_session: Session = None,
        work_id: int = None,
        document_id: int = None,
        oddpub_host_api: str = config.ODDPUB_HOST_API,
    ):
        """
        Initialize the OddpubWrapper.

        Args:
            db (Session, optional): SQLAlchemy database session
            work_id (int): ID of the work being processed
            document_id (int): ID of the document being processed
        """
        try:
            self.oddpub_host_api = oddpub_host_api
            self.db_session = db_session
            self.work_id = work_id
            self.document_id = document_id
            logger.info("Successfully initialized OddpubWrapper")
        except Exception as e:
            logger.error(f"Failed to initialize OddpubWrapper: {str(e)}")
            raise

    def process_pdfs(
        self, pdf_folder: str, force_upload: bool = False
    ) -> OddpubMetrics:
        """
        Process PDFs through the complete ODDPub workflow and store results in database.

        Args:
            pdf_folder (str): Path to folder containing PDF files
            force_upload (bool): Skip confirmation prompt if True (-y flag)

        Returns:
            OddpubMetrics: Results of open data analysis
        """
        try:
            results = []
            # Iterate over each PDF file in the folder
            for pdf_file in Path(pdf_folder).glob("*.pdf"):
                logger.info(f"Processing {pdf_file.name}...")
                with open(pdf_file, "rb") as f:
                    response = requests.post(
                        f"{self.oddpub_host_api}/oddpub", files={"file": f}
                    )
                    response.raise_for_status()

                    r_result = response.json()
                    results.append((pdf_file.name, r_result))

            # Display results summary
            logger.info("Results Summary:")
            for filename, result in results:
                logger.info(f"\n{filename}:")
                for key, value in result.items():
                    logger.info(f"  {key}: {value}")

            # Ask for confirmation before database upload
            if not force_upload:
                confirm = input(
                    "\nDo you want to upload these results to the database? (y/N): "
                )
                if confirm.lower() != "y":
                    logger.info("Database upload cancelled by user")
                    return None

            # Upload to database
            for _, r_result in results:
                oddpub_metrics = OddpubMetrics(**r_result)
                oddpub_metrics.work_id = self.work_id
                oddpub_metrics.document_id = self.document_id
                self.db_session.add(oddpub_metrics)

            self.db_session.commit()
            logger.info(f"Successfully processed and uploaded {len(results)} files")
            return oddpub_metrics

        except Exception as e:
            logger.error(f"Error in PDF processing workflow: {str(e)}")
            self.db_session.rollback()

    def process_s3_inventory(self, s3_bucket: str, inventory_prefix: str):
        """
        Process S3 inventory to sync with the database and generate Oddpub metrics.

        Args:
            s3_bucket (str): Name of the S3 bucket
            inventory_prefix (str): Prefix of the inventory files in the S3 bucket
        """
        try:
            s3_client = boto3.client("s3")
            paginator = s3_client.get_paginator("list_objects_v2")
            page_iterator = paginator.paginate(
                Bucket=s3_bucket, Prefix=inventory_prefix
            )

            existing_hashes = {
                doc.hash_data
                for doc in self.db_session.query(Documents.hash_data).all()
            }
            s3_hashes = set()

            for page in page_iterator:
                for obj in page.get("Contents", []):
                    key = obj["Key"]
                    if key.endswith(".pdf"):
                        response = s3_client.get_object(Bucket=s3_bucket, Key=key)
                        file_content = response["Body"].read()
                        file_hash = hashlib.sha256(file_content).hexdigest()
                        s3_hashes.add(file_hash)

                        if file_hash not in existing_hashes:
                            # Create new document entry
                            document = Documents(
                                hash_data=file_hash, s3uri=f"s3://{s3_bucket}/{key}"
                            )
                            self.db_session.add(document)
                            self.db_session.commit()

                            # Create new work entry
                            work = Works(
                                initial_document_id=document.id,
                                primary_document_id=document.id,
                            )
                            self.db_session.add(work)
                            self.db_session.commit()

                            # Create new provenance entry
                            provenance = Provenance(
                                pipeline_name="S3 Inventory Sync", version="1.0"
                            )
                            self.db_session.add(provenance)
                            self.db_session.commit()

                            # Update work and document with provenance_id
                            work.provenance_id = provenance.id
                            document.provenance_id = provenance.id
                            self.db_session.commit()

                            # Run Oddpub analysis
                            self.work_id = work.id
                            self.document_id = document.id
                            self.process_pdfs(
                                pdf_folder=f"s3://{s3_bucket}/{key}", force_upload=True
                            )

            # Remove documents not in S3
            missing_hashes = existing_hashes - s3_hashes
            for missing_hash in missing_hashes:
                document = (
                    self.db_session.query(Documents)
                    .filter_by(hash_data=missing_hash)
                    .first()
                )
                if document:
                    self.db_session.delete(document)
                    self.db_session.commit()

            logger.info("S3 inventory processing completed successfully")

        except Exception as e:
            logger.error(f"Error processing S3 inventory: {str(e)}")
            self.db_session.rollback()
