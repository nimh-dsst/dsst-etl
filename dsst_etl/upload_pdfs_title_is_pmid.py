import hashlib

import boto3
import requests
import sqlalchemy

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

    def process_s3_bucket(self) -> str:
        try:
            page_iterator = self._get_s3_page_iterator()
            existing_hashes = self._get_existing_hashes()
            provenance = self._create_provenance_entry()

            for page in page_iterator:
                self._process_page(page, existing_hashes, provenance)

            self.db_session.commit()
            logger.info("S3 inventory processing completed successfully")

        except Exception as e:
            logger.error(f"Error processing S3 inventory: {str(e)}")

    def _get_s3_page_iterator(self):
        paginator = self.s3_client.get_paginator("list_objects_v2")
        return paginator.paginate(Bucket=self.bucket_name)

    def _get_existing_hashes(self):
        return {
            doc.hash_data for doc in self.db_session.query(Documents.hash_data).all()
        }

    def _create_provenance_entry(self):
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

    def _process_page(self, page, existing_hashes, provenance):
        for obj in page.get("Contents", []):
            key = obj["Key"]
            if not key.endswith(".pdf"):
                continue

            response = self.s3_client.get_object(Bucket=self.bucket_name, Key=key)
            file_content = response["Body"].read()
            try:
                file_hash = hashlib.sha256(file_content).hexdigest()
            except Exception as e:
                logger.error(f"Error hashing file: {str(e)}")
                continue
            if file_hash in existing_hashes:
                continue

            self._create_document_entries(key, file_content, file_hash, provenance)

    def _create_document_entries(self, key, file_content, file_hash, provenance):
        try:
            document = Documents(
                hash_data=file_hash,
                s3uri=f"s3://{self.bucket_name}/{key}",
                provenance_id=provenance.id,
            )
            self.db_session.add(document)

            work = Works(
                initial_document_id=document.id,
                primary_document_id=document.id,
                provenance_id=provenance.id,
            )
            self.db_session.add(work)
            self.db_session.commit()
            identifier = Identifier(
                pmid=key.split("/")[-1].split(".")[0],
                document_id=document.id,
                provenance_id=provenance.id,
            )
            self.db_session.add(identifier)
            self.db_session.commit()
        except Exception as e:
            logger.error(f"Error creating document entries: {str(e)}")

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
