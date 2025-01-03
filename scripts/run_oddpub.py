import argparse
from dsst_etl import get_db_engine
from dsst_etl.db import get_db_session
from dsst_etl.oddpub_wrapper import OddpubWrapper  

def main():
    parser = argparse.ArgumentParser(description="Process PDFs with OddpubWrapper")
    parser.add_argument('pdf_folder', type=str, help='Path to the folder containing PDF files')
    args = parser.parse_args()

    oddpubWrapper = OddpubWrapper(get_db_session(get_db_engine()))
    oddpubWrapper.process_pdfs(args.pdf_folder)

if __name__ == "__main__":
    main()

