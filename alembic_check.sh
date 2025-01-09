#!/bin/bash

# Load environment variables if .env exists
if [ -f .env ]; then
    echo "Loading variables from .env file..."
    export $(cat .env | grep -v '^#' | xargs)
elif [ -f .mockenv ]; then
    echo "Copy values from .mockenv to .env and load them"
    cp .mockenv .env
    export $(cat .env | grep -v '^#' | xargs)
else
    echo "Warning: Neither .env nor .mockenv file found!"
fi



# Run alembic check
echo "Running alembic check..."
alembic upgrade heads
alembic check

# Store the exit code
exit_code=$?

# Show the result
if [ $exit_code -eq 0 ]; then
    echo "✅ Alembic check passed successfully"
else
    echo "❌ Alembic check failed with exit code $exit_code"
fi

# Return the alembic check exit code
exit $exit_code
