from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from dsst_etl.config import config
from dsst_etl.oddpub_wrapper import OddpubWrapper

# Database setup
engine = create_engine(config.DATABASE_URI)
Session = sessionmaker(bind=engine)
session = Session()

# Initialize OddpubWrapper
oddpub_wrapper = OddpubWrapper(db_session=session)

# Process S3 inventory
s3_bucket = "your-s3-bucket-name"
inventory_prefix = "your-inventory-prefix"
oddpub_wrapper.process_s3_inventory(s3_bucket, inventory_prefix)
