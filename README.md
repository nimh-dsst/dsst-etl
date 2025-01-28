# DSST-ETL

A collection of scripts for extracting, transforming, and loading data.

## Development setup

The following will allow you to run the scripts in this project:

### install uv

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
# install all dependencies
uv sync --all-extras
# copy the mock environment variables to the file used by docker compose and the package
cp .mockenv .env
# activate the virtual environment
source .venv/bin/activate
```

The scripts will have different requirements for resource access (s3 buckets, Postgres DB, internet, APIs, etc.)

Instead of accessing the centralized Postgres server used for sharing you can deploy one locally using docker:

```bash
docker compose -f .docker/postgres-compose.yaml up -d
```

## Other development notes

### Tidying the local database resources

The following will remove the postgres container and its associated volume (the -v flag).

```bash
docker compose -f .docker/postgres-compose.yaml down -v
```

### Install the pre-commit hooks

If you are developing locally you should make use of pre-commit hooks to ensure that your code is formatted correctly and passes linting checks.

```bash
pre-commit install
# run the pre-commit hooks on all files
   pre-commit run --all-files
```

### Run the tests

You can run the test suite (assuming you have activated the virtual environment and set up required resources) with the following command:

```bash
pytest
```

### Database Setup

To set up the database for this project, follow these steps:

1. **Create the Database**:
   - If the database does not exist, you need to create it. This can be done using a database client or command line tool specific to your database system. For example, using PostgreSQL, you might run:

     ```bash
     createdb your_database_name
     ```

2. **Initialize the Database Schema**:
   - Once the database is created, you need to apply the database schema using Alembic. Run the following command to apply all migrations:

     ```bash
     alembic upgrade head
     ```

   - This command will apply all pending migrations and set up the database schema as defined in your Alembic migration scripts.

3. **Verify the Setup**:
   - After running the migrations, verify that the database schema is correctly set up by checking the tables and their structures.

### Database Migrations

This project uses Alembic for database migrations. Follow the steps below to generate and apply migrations to the database.

#### Prerequisites

- Ensure your database is running. If you're using Docker, you can start the database with:

  ```bash
  docker-compose -f .docker/postgres-compose.yaml up -d
  ```

#### Running Migrations

1. **Configure Alembic**: Ensure that the `alembic/env.py` file is correctly set up to connect to your database. The connection settings are managed through environment variables in your `.env` file.

2. **Create a New Migration**: To create a new migration script, run the following command:

   ```bash
   alembic revision --autogenerate -m "Description of changes"
   ```

   This will generate a new migration script in the `alembic/versions` directory.

3. **Review the Migration Script**: Open the generated migration script and review it to ensure it accurately reflects the changes you want to make to the database schema.

4. **Apply the Migration**: To apply the migration to the database, run:

   ```bash
   alembic upgrade head
   ```

   This command will apply all pending migrations up to the latest one.

5. **Verify the Database**: Check your database to ensure that the schema has been updated as expected.

#### Troubleshooting

- If you encounter any issues, ensure that your database connection settings in the `.env` file are correct.
- Check the Alembic logs for any error messages that might indicate what went wrong.

For more detailed information on using Alembic, refer to the [Alembic documentation](https://alembic.sqlalchemy.org/en/latest/).

### Database Maintenance

The shared database is deployed using OpenTofu (see the terraform directory).

A connection example (adding db password and address as required):

```bash
PGPASSWORD=<password> psql -h <host> -U postgres -d dsst_etl -c "\l"
```

To list snapshots:

```bash
aws rds describe-db-snapshots --db-instance-identifier dsst-etl-postgres-prod --query 'DBSnapshots[*].{SnapshotId:DBSnapshotIdentifier,SnapshotType:SnapshotType,Status:Status,Created:SnapshotCreateTime}'
```

To manually create a snapshot:

```bash
aws rds create-db-snapshot \
    --db-instance-identifier dsst-etl-postgres-prod \
    --db-snapshot-identifier dsst-etl-postgres-prod-manual-1
```

To delete a snapshot:

```bash
aws rds delete-db-snapshot \
    --db-snapshot-identifier dsst-etl-postgres-prod-manual-1
```

## Script descriptions

### get_ipids.py

#### 'IC': Institute or Center abbreviation

- Values are defined in the list 'ICs', which includes abbreviations for various NIH institutes and centers.

### 'YEAR': Year of the data

- Each 'IC' and year combination is used to make a request to the NIH website to retrieve data.

### 'IPID': Intramural Program Integrated Data (unique identifier)

- Values are obtained by scraping the NIH website using a POST request with specific parameters ('ic' and 'searchyear').

  - Regular expression (re.findall) is used to extract IPID numbers from the response text.
  - For each unique IPID, a row with 'IC', 'YEAR', and 'IPID' is added to the CSV, avoiding duplicates.

### get_pmids.py

#### 'PI': Principal Investigator(s)

- The 'headings' and 'showname' HTML elements are searched for relevant labels to extract the names of Principal Investigators.

#### 'PMID': PubMed ID

- A regular expression is used to find patterns matching PubMed IDs in the HTML content.

#### 'DOI': Digital Object Identifier

- A regular expression is used to find patterns matching DOI values in the HTML content.

#### 'PROJECT': Project associated with the report

- Extracted from the 'contentlabel' HTML element within the reports.

### get_pmids_articles.py

#### 'pmids_articles.csv': Filtered CSV containing articles that meet specific criteria

- Removes publications with types: ['Review', 'Comment', 'Editorial', 'Published Erratum'].
- Only includes publications identified as articles based on PubMed API data.

### data_conversion.py

#### Fetches information for PubMed articles, specifically titles and journal names

- 'pmid': PubMed ID (unique identifier for a publication in PubMed).
- 'title': Title of the PubMed article.
- 'journal': Name of the journal in which the article was published.
- Errors during the fetch process are logged, and corresponding entries in the CSV have empty strings for title and journal.

### Data Retrieval Process

- The program reads an existing CSV file ('pmids_articles.csv') containing PubMed IDs ('PMID').
- For each unique PubMed ID, it uses the Metapub library to fetch additional details, including the article title and journal.
- If an error occurs during the fetch process, the program records the PubMed ID and assigns empty strings to title and journal.

## filter_cli.py

- Takes an input directory and parses all *.pdf files in specified directory.
- Take an output CSV filepath and generates a table of pdf metadata and whether the PDF document contains the phrase "HHS Public Access" on the first page of the PDF. NOTE: the HHS public access versions of manuscripts  have "Antenna House" in the producer metadata for the test set. The creater metadata references either "Antenna House" or "AH" in the test set. This may be useful for cross-validation, but has not been tested with a large data set (test set n~3400 files).
- To only install dependencies for filter_cli.py please `pip install -r filter_requirements.txt`.

## R Script Dependencies

Currently using `renv` for package management.

### Packages

#### Binary installations

- Pandoc. [Installation Instructions](https://pandoc.org/installing.html). Required for [rtransparent](https://github.com/serghiou/rtransparent) packages's vignettes.
- pdftotext. Install [Poppler](https://poppler.freedesktop.org/). For macOS use Homebrew: `brew install poppler`. See the OS Dependcies section on the [PYPI pdftotext module](https://pypi.org/project/pdftotext/) for other OS installations of Poppler.

#### R Packages

##### CRAN

- devtools
  - Needed for installing packaged hosted on GitHub.
_ renv
  - Needed for loading R project environment so users do not need to manually install packages. *TODO: Add in section on using renv to load dependencies.*

##### GitHub

- [Open Data Detection in Publications (ODDPub)](https://github.com/quest-bih/oddpub). Required for [rtransparent](https://github.com/serghiou/rtransparent). *Must us v6.0!* If installing manually run `devtools::install_github("quest-bih/oddpub@v6")`. Updated ODDPub uses different parameters in latest version than is
- [CrossRef Minter (crminer)](https://github.com/cran/crminer). Required for [metareadr](https://github.com/serghiou/metareadr)
_ [Meta Reader (metareadr)](https://github.com/serghiou/metareadr). Required for [rtransparent](https://github.com/serghiou/rtransparent).
