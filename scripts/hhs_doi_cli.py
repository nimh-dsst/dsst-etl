import argparse
import csv
from pathlib import Path
from typing import Generator

import pypdf
from pypdf._doc_common import DocumentInformation
from pypdf.errors import EmptyFileError, PdfStreamError
import pdf2doi
from pdf2doi import config as pdf2doi_config
from tqdm import tqdm


def extract_pdf_metadata(
    pdf_dir: Path,
    output_csv: Path,
    new_run: bool = False,
    make_filelist: bool = True,
    pdf2doi_verbose: bool = False,
) -> None:
    """
    Extract metadata from PDFs in a specified directory and save to a CSV file.

    Parameters
    ----------
    pdf_dir : Path
        Directory containing PDF files to process.
    output_csv : Path
        Path to the CSV file where extracted metadata will be saved.
    new_run : bool, optional
        If True, raises an error if the output CSV file already exists.
        Defaults to False.
    make_filelist : bool, optional
        If True, generates a list of all PDFs before processing.
        This allows tqdm to show a total count but uses more memory.
        Defaults to True.
    pdf2doi_verbose : bool, optional
        If True, enables verbose output from the `pdf2doi` library.
        Defaults to False.

    Returns
    -------
    None
        This function writes results directly to the specified CSV file.

    Raises
    ------
    FileExistsError
        If `new_run` is True and the output CSV file already exists.
    """
    if pdf2doi_verbose:
        pdf2doi_config.set("verbose", True)
    else:
        pdf2doi_config.set("verbose", False)

    output_exists: bool = output_csv.exists()

    if output_exists and new_run is False:
        print("Removing previously processed PDFs")
        filenames: list[Path] = []
        with open(output_csv, "r") as file:
            csv_dict_reader = csv.DictReader(file)
            for row in csv_dict_reader:
                if row["identifier_type"] == "DOI":
                    filenames.append(Path(row["name"]).relative_to(Path.cwd()))
                else:
                    continue
        previously_found: set[Path] = set(filenames)
        pdfs: list[Path] | Generator[Path] = list(
            set(list(pdf_dir.rglob("*.[pP][dD][fF]"))) - previously_found
        )
        print(f"Found {len(previously_found)} previously processed PDFs")
        if len(pdfs) == 0:
            print(f"All PDFs already accounted for in {output_csv}!")
            return None
    elif output_exists and new_run is True:
        raise FileExistsError(
            f"{output_csv} exists and new_run is True."
            + " Please remove existing file prior to a new run!"
        )
    else:
        # keep a generator for memory management
        pdfs = pdf_dir.rglob("*.[pP][dD][fF]")
        if make_filelist:
            pdfs = list(pdfs)

    dicts: list[dict] = []
    with open(output_csv, "a") as f_out:
        fieldnames: list[str] = [
            "identifier",
            "identifier_type",
            "extraction_method",
            "name",
            "producer",
            "creator",
            "header",
            "has_hhs_text",
            "error",
        ]
        writer: csv.DictWriter = csv.DictWriter(
            f_out, fieldnames, quoting=csv.QUOTE_NONNUMERIC, escapechar="\\"
        )
        if not output_exists:
            writer.writeheader()

        for pdf in tqdm(pdfs):
            try:
                # Extract DOI
                try:
                    doi_results = pdf2doi.pdf2doi(str(pdf.absolute()))
                    # Get the first result if multiple are returned
                    doi_info = (
                        doi_results[0] if isinstance(doi_results, list) else doi_results
                    )
                    identifier = doi_info.get("identifier")
                    identifier_type = doi_info.get("identifier_type")
                    extraction_method = doi_info.get("method")
                except Exception:
                    identifier = None
                    identifier_type = None
                    extraction_method = None

                with open(pdf, "rb") as file:
                    pdf_reader = pypdf.PdfReader(file)
                    metadata = pdf_reader.metadata
                    try:
                        page = pdf_reader.pages[0]
                        text = page.extract_text()
                        has_hhs_text: bool = "HHS Public Access" in text
                    except Exception as e:
                        pdf_info: dict = {
                            "identifier": identifier,
                            "identifier_type": identifier_type,
                            "extraction_method": extraction_method,
                            "name": pdf.absolute(),
                            "producer": None,
                            "creator": None,
                            "header": None,
                            "has_hhs_text": None,
                            "error": str(e),
                        }
                        dicts.append(pdf_info)
                        continue

                    if isinstance(metadata, DocumentInformation):
                        pdf_info = {
                            "identifier": identifier,
                            "identifier_type": identifier_type,
                            "extraction_method": extraction_method,
                            "name": pdf.absolute(),
                            "producer": metadata.producer,
                            "creator": metadata.creator,
                            "header": pdf_reader.pdf_header,
                            "has_hhs_text": has_hhs_text,
                            "error": None,
                        }
                    else:
                        pdf_info = {
                            "identifier": identifier,
                            "identifier_type": identifier_type,
                            "extraction_method": extraction_method,
                            "name": pdf.absolute(),
                            "producer": None,
                            "creator": None,
                            "header": None,
                            "has_hhs_text": has_hhs_text,
                            "error": "No metadata",
                        }
            except (PdfStreamError, OSError, EmptyFileError) as e:
                pdf_info = {
                    "identifier": None,
                    "identifier_type": None,
                    "extraction_method": None,
                    "name": pdf.absolute(),
                    "producer": None,
                    "creator": None,
                    "header": None,
                    "has_hhs_text": None,
                    "error": str(e),
                }

            writer.writerow(pdf_info)
    print(f"Metadata extracted to {output_csv}")


def main():
    """
    CLI entry point for extracting metadata from PDFs.

    This function parses command-line arguments to specify the input directory,
    output CSV file, and other configuration options, then processes the PDFs
    accordingly.

    Parameters
    ----------
    None

    Returns
    -------
    None
        This function is designed to be run from the command line and does not
        return any value.

    Command-Line Arguments
    ----------------------
    -i, --input-dir : Path, optional
        Directory containing PDF files to process. Defaults to './2024_all_ics/pdfs'.
    -o, --output : Path, optional
        Path to the output CSV file. Defaults to './has_hhs.csv'.
    -n, --new-run : bool, optional
        If True, ignores any existing output CSV file. Defaults to False.
    -m, --make-filelist : bool, optional
        If True, generates a file list before processing for tqdm to show progress.
        Defaults to False.
    -v, --verbose : bool, optional
        If True, enables verbose output from the `pdf2doi` library. Defaults to False.

    Raises
    ------
    ValueError
        If the specified input directory does not exist.
    """
    parser = argparse.ArgumentParser(
        description="Extract metadata from PDFs in a directory."
    )
    parser.add_argument(
        "-i",
        "--input-dir",
        type=Path,
        default=Path("./2024_all_ics/pdfs"),
        help="Directory containing PDF files (default: ./2024_all_ics/pdfs)",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=Path("./has_hhs.csv"),
        help="Output CSV file path (default: ./has_hhs.csv)",
    )
    parser.add_argument(
        "-n",
        "--new-run",
        action="store_true",
        help="Ignore existing output CSV file if it exists",
    )
    parser.add_argument(
        "-m",
        "--make-filelist",
        action="store_true",
        help="Make filelist prior to for loop."
        + "Allows tqdm to provide total but must keep filelist in memory.",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Print proccessing output from pdf2doi",
    )
    args = parser.parse_args()

    # Validate input directory exists
    if not args.input_dir.is_dir():
        print(f"Error: Input directory {args.input_dir} does not exist.")
        return

    extract_pdf_metadata(
        args.input_dir,
        args.output,
        new_run=args.new_run,
        make_filelist=args.make_filelist,
        pdf2doi_verbose=args.verbose,
    )


if __name__ == "__main__":
    main()
