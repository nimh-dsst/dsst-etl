import argparse
from dsst_etl.db import get_db_session
from dsst_etl.upload_rtransparent_data import RTransparentDataUploader  


def main():
    parser = argparse.ArgumentParser(description='Upload RTransparent data from a file.')
    parser.add_argument('input_file', type=str, help='Path to the input file (feather or parquet)')
    
    args = parser.parse_args()
    
    uploader = RTransparentDataUploader(get_db_session())
    
    uploader.upload_data(args.input_file)

if __name__ == "__main__":
    main()

