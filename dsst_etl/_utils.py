from pathlib import Path

from .config import config


def get_compute_context_id():
    return hash(f"{config.HOSTNAME}_{config.USERNAME}")


def get_bucket_name():
    bucket_name = config.S3_BUCKET_NAME
    if not bucket_name:
        raise ValueError("S3_BUCKET_NAME environment variable is not set")
    return bucket_name


def convert_metadata_to_identifier(metadata: dict) -> dict:
    """
    Convert the metadata dictionary to a format where the keys are filenames
    and the values are dictionaries containing 'PMID', 'DOI', and 'PMCID'.

    Args:
        metadata (dict): The original metadata dictionary for the documents.

    Returns:
        dict: The transformed metadata dictionary.
    """
    transformed_metadata = {}
    for _, data in metadata.items():
        for pdf in data["pdfs"]:
            filename = Path(pdf["filepath"]).name
            transformed_metadata[filename] = {
                "PMID": pdf["PMID"],
                "DOI": pdf["DOI"],
                "PMCID": pdf["PMCID"],
            }
    return transformed_metadata
