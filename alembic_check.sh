#!/bin/bash

# Exit immediately if any command fails
set -e

# Run the Alembic check command
alembic check

if [ $? -ne 0 ]; then
    echo "Error: Uncommitted Alembic upgrade operations detected."
    echo "Please generate and commit your migration scripts."
    exit 1
fi

echo "Alembic check passed. No new upgrade operations detected."
