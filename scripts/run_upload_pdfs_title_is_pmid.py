import argparse
from dsst_etl import get_db_engine, logger
from dsst_etl.db import get_db_session
from dsst_etl.upload_pdfs_title_is_pmid import UploadPDFsTitleIsPMID

def main():
    db_session = get_db_session(get_db_engine())
    
    try:
        uploader = UploadPDFsTitleIsPMID(db_session)
        uploader.run()
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
    finally:
        db_session.close()


if __name__ == "__main__":
    main()