import logging
import sys

# Create a logger
logger = logging.getLogger("dsst_etl")
logger.setLevel(logging.DEBUG)  # Set the log level to DEBUG for detailed output

# Create a console handler
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.DEBUG)

# Create a formatter and set it for the handler
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
console_handler.setFormatter(formatter)

# Add the handler to the logger
logger.addHandler(console_handler)

# Optionally, add a file handler if you want to log to a file
file_handler = logging.FileHandler("dsst_etl.log")
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
