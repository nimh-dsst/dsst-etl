import numpy as np
import pandas as pd
import sqlalchemy
from tqdm import tqdm

from dsst_etl.logger import logger
from dsst_etl.models import Provenance, RTransparentPublication, Works


class RTransparentDataUploader:
    """
    Handles uploading RTransparent metrics data to the database.

    This class manages:
    1. Reading data from Feather or Parquet files
    2. Creating RTransparentPublication records
    3. Creating and linking Works and Provenance records
    """

    def __init__(self, db_session: sqlalchemy.orm.Session):
        """
        Initialize the uploader with a database connection.

        Args:
            db_url (str): Database connection URL
        """
        self.db_session = db_session

    def upload_data(self, file_path, n_rows=1000):
        """
        Upload data from a file to the database.

        Args:
            file_path (str): Path to the input file (Feather or Parquet)
            n_rows (int): Number of rows to process in each batch
        """
        # Read the input file
        data = self._read_file(file_path)
        logger.info(f"Read {len(data)} rows from {file_path}")
        logger.info(f"Processing {n_rows} rows at a time")
        logger.info("Starting to process data")

        # Process data in chunks
        for start in tqdm(range(0, len(data), n_rows), desc="Processing data"):
            chunk = data.iloc[start : start + n_rows]
            # Create entries for RTransparentPublication
            publications = []
            for _, row in chunk.iterrows():
                # Convert numpy.ndarray to string
                row_dict = row.to_dict()
                if isinstance(row_dict.get("funder"), np.ndarray):
                    row_dict["funder"] = ", ".join(row_dict["funder"].tolist())

                publication = RTransparentPublication(**row_dict)
                publications.append(publication)

                # Create and reference entries in Works and Provenance as needed
                # provenance = self._create_provenance_record(session, row)
                # work = self._create_work_record(session, publication, provenance)

                # Explicitly handle the fact that “Document” doesn’t exist here
                # because we don’t have the source pdf. This may simply be a comment
                # in the code with reasoning on the reference value/null value used.
                publication.work_id = None
                publication.provenance_id = None

            # Bulk insert publications
            self.db_session.bulk_save_objects(publications)
            self.db_session.commit()

        self.db_session.close()

    def _read_file(self, file_path):
        """
        Read data from a Feather or Parquet file.

        Args:
            file_path (str): Path to the input file

        Returns:
            DataFrame: Loaded data
        """
        if file_path.endswith(".feather"):
            return pd.read_feather(file_path)
        elif file_path.endswith(".parquet"):
            return pd.read_parquet(file_path)
        else:
            raise ValueError(
                "Unsupported file format. Please provide a Feather or Parquet file."
            )

    def _create_provenance_record(self, session, row):
        """
        Create a provenance record for a data row.

        Args:
            session (Session): Database session
            row (Series): Data row

        Returns:
            Provenance: Created provenance record
        """
        provenance = Provenance(
            pipeline_name="RTransparent Data Upload",
            version="1.0",
            compute="Compute Context",
            personnel="Uploader",
            comment=row.get("comment", "No comment provided"),
        )
        session.add(provenance)
        session.flush()  # Ensure the ID is available
        return provenance

    def _create_work_record(self, session, publication, provenance):
        """
        Create a work record linked to a publication and provenance.

        Args:
            session (Session): Database session
            publication (RTransparentPublication): Publication record
            provenance (Provenance): Provenance record

        Returns:
            Works: Created work record
        """
        work = Works(
            initial_document_id=None,  # No document available
            primary_document_id=None,  # No document available
            provenance_id=provenance.id,
        )
        session.add(work)
        session.flush()  # Ensure the ID is available
        return work
