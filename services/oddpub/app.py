import logging
from pathlib import Path
from typing import Dict, List

import pandas as pd
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
import shutil
import os
import rpy2.robjects as robjects
from rpy2.robjects import pandas2ri
from rpy2.robjects.packages import importr
from dataclasses import dataclass, asdict

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

logger = logging.getLogger(__name__)

app = FastAPI()


@dataclass
class OddpubMetrics:
    article: str
    is_open_data: bool
    open_data_category: str
    is_reuse: bool
    is_open_code: bool
    is_open_data_das: bool
    is_open_code_cas: bool
    das: str
    open_data_statements: str
    cas: str
    open_code_statements: str

    def serialize(self) -> dict:
        """
        Serialize the OddpubMetrics instance to a dictionary.
        Returns:
            dict: A dictionary representation of the OddpubMetrics instance.
        """
        return asdict(self)


class OddpubWrapper:
    """
    A wrapper class for calling ODDPub R functions from Python using rpy2.
    """

    def __init__(self):
        """
        Initialize the OddpubWrapper.
        Args:
            db (Session, optional): SQLAlchemy database session
            work_id (int): ID of the work being processed
            document_id (int): ID of the document being processed
        """
        try:
            self.base = importr("base")
            self.oddpub = importr("oddpub")
            pandas2ri.activate()
            logger.info("Successfully initialized OddpubWrapper")
        except Exception as e:
            logger.error(f"Failed to initialize OddpubWrapper: {str(e)}")
            raise

    def _convert_pdfs(self, pdf_folder: str, output_folder: str) -> None:
        """Convert PDFs to text using oddpub::pdf_convert."""
        try:
            r_pdf_folder = robjects.StrVector([str(Path(pdf_folder))])
            r_output_folder = robjects.StrVector([str(Path(output_folder))])

            logger.info(f"Converting PDFs from {r_pdf_folder} to text in {r_output_folder}")
            self.oddpub.pdf_convert(pdf_folder, output_folder)
            logger.info(
                f"Successfully converted PDFs from {pdf_folder} to text in {output_folder}"
            )
        except Exception as e:
            logger.error(f"Error in PDF conversion: {str(e)}")
            raise e

    def _load_pdf_text(self, pdf_text_folder: str) -> robjects.vectors.ListVector:
        """Load converted PDF text using oddpub::pdf_load."""
        try:
            pdf_text_sentences = self.oddpub.pdf_load(pdf_text_folder)
            logger.info(f"Successfully loaded PDF text from {pdf_text_folder}")
            return pdf_text_sentences
        except Exception as e:
            logger.error(f"Error in loading PDF text: {str(e)}")
            raise

    def _search_open_data(
        self, pdf_text_sentences: robjects.vectors.ListVector
    ) -> List[OddpubMetrics]:
        """Search for open data statements using oddpub::open_data_search."""
        try:
            open_data_results = self.oddpub.open_data_search(pdf_text_sentences)
            result = self._convert_r_result(open_data_results)
            logger.info("Successfully completed open data search")
            return result
        except Exception as e:
            logger.error(f"Error in open data search: {str(e)}")
            raise

    def _cleanup_output_folder(self, output_folder: str) -> None:
        """Remove the temporary output folder and its contents."""
        try:
            shutil.rmtree(output_folder)
            logger.info(f"Successfully cleaned up output folder: {output_folder}")
        except Exception as e:
            logger.error(f"Error cleaning up output folder: {str(e)}")
            raise

    def process_pdfs(self, pdf_folder: str) -> Dict:
        """
        Process PDFs through the complete ODDPub workflow and store results in database.
        Args:
            pdf_folder (str): Path to folder containing PDF files
            output_folder (str): Path to temporary output folder for converted text files
        Returns:
            OddpubMetrics: Results of open data analysis
        """
        try:
            # Create output directory if it doesn't exist
            output_folder = "oddpub_output/"
            Path(output_folder).mkdir(parents=True, exist_ok=True)

            # Execute the workflow
            logger.info(f"Converting PDFs from {pdf_folder} to text in {output_folder}")

            self._convert_pdfs(pdf_folder, output_folder)
            pdf_text_sentences = self._load_pdf_text(output_folder)
            result = self._search_open_data(pdf_text_sentences)

            return result
        except Exception as e:
            logger.error(f"Error in PDF processing workflow: {str(e)}")
        finally:
            # Attempt cleanup even if processing failed
            self._cleanup_output_folder(output_folder)

    def _convert_r_result(self, r_result) -> OddpubMetrics:
        """Convert R results to OddpubMetrics instance."""
        try:
            df = pandas2ri.rpy2py(r_result)
            result_dict = df.to_dict("records")[0] if not df.empty else {}

            # Create new OddpubMetrics instance with relationships
            oddpub_metrics = OddpubMetrics(
                article=result_dict.get("article"),
                is_open_data=result_dict.get("is_open_data", False),
                open_data_category=result_dict.get("open_data_category"),
                is_reuse=result_dict.get("is_reuse", False),
                is_open_code=result_dict.get("is_open_code", False),
                is_open_data_das=result_dict.get("is_open_data_das", False),
                is_open_code_cas=result_dict.get("is_open_code_cas", False),
                das=result_dict.get("das"),
                open_data_statements=result_dict.get("open_data_statements"),
                cas=result_dict.get("cas"),
                open_code_statements=result_dict.get("open_code_statements"),
            )
            return oddpub_metrics
        except Exception as e:
            logger.error(f"Error converting R result: {str(e)}")
            raise


@app.post("/oddpub")
def process_pdf(file: UploadFile = File(...)):
    pdf_folder = "/tmp/pdfs/"
    Path(pdf_folder).mkdir(parents=True, exist_ok=True) 

    file_location = f"{pdf_folder}/{file.filename}"
    logger.info(f"Saving file to {file_location}")  

    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    oddpub_wrapper = OddpubWrapper()

    result = oddpub_wrapper.process_pdfs(pdf_folder)

    os.remove(file_location)

    return JSONResponse(content=result.serialize())
