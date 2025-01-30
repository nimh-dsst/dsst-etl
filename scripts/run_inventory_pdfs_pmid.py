import argparse
from dsst_etl import get_db_engine, logger
from dsst_etl.db import get_db_session
from dsst_etl.inventory_pdfs_pmid import DocumentInventoryPMID

def main():
    db_session = get_db_session(get_db_engine())
    
    try:
        inventory = DocumentInventoryPMID(db_session)
        inventory.run()
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
    finally:
        db_session.close()


if __name__ == "__main__":
    main()