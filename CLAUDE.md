# CLAUDE.md - Project Context for Claude Code

## Project Overview

**DSST-ETL** (Data Science and Sharing Team - Extract Transform Load) is an NIMH initiative for building infrastructure to extract, process, and manage scientific publication data. The project focuses on tracking open science practices in NIH intramural research publications.

## Repository Purpose

This repository provides:
1. Scripts to scrape publication data from NIH intramural research programs
2. Database infrastructure (PostgreSQL) for storing publication metadata
3. S3 integration for PDF document storage
4. Containerized services for analyzing publications (ODDPub for open data detection)
5. Terraform/OpenTofu configurations for AWS infrastructure

## Key Technologies

- **Python**: Primary language, managed with `uv`
- **PostgreSQL**: Database (local Docker + AWS RDS)
- **SQLAlchemy + Alembic**: ORM and migrations
- **AWS**: S3 (storage), RDS (database)
- **Docker/Podman**: Container runtime
- **Apptainer**: HPC container runtime (Biowulf)
- **R**: ODDPub analysis tool
- **FastAPI**: API wrapper for ODDPub service

## Project Structure

```
dsst-etl/
├── dsst_etl/           # Main Python package
│   ├── models.py       # SQLAlchemy database models
│   ├── upload_pdfs.py  # PDF upload and processing
│   ├── config.py       # Configuration management
│   └── _utils.py       # Utility functions
├── alembic/            # Database migrations
├── scripts/            # CLI scripts
├── services/           # Docker services (ODDPub)
├── terraform/          # AWS infrastructure as code
├── tests/              # pytest test suite
├── docs/               # Documentation
└── .docker/            # Docker compose files
```

## Database Schema

Key tables:
- **documents**: PDF file metadata (hash, S3 URI, work reference)
- **works**: Academic publications (may have multiple documents)
- **provenance**: Audit trail for data operations
- **identifiers**: PMID, PMCID, DOI mappings
- **oddpub_metrics**: Open data/code detection results

## Development Commands

```bash
# Setup
uv sync --all-extras
cp .mockenv .env
source .venv/bin/activate

# Local database
docker compose -f .docker/postgres-compose.yaml up -d

# Run migrations
alembic upgrade head

# Run tests
pytest

# Pre-commit hooks
pre-commit install
pre-commit run --all-files
```

## AWS Resources

- **S3 Bucket**: See SSM `/dsst-etl/S3_BUCKET_NAME`
- **RDS Instance**: See SSM `/dsst-etl/POSTGRES_HOST`
- **Region**: `us-east-1`
- **AWS Profile**: `nimh-irp`

### SSM Parameter Store
Secrets are stored in AWS SSM Parameter Store under `/dsst-etl/`:
```bash
# Retrieve secrets (requires MFA session)
aws ssm get-parameters-by-path --path "/dsst-etl/" --with-decryption
```

## Related Repositories

- `osm`: Open Science Metrics core calculations
- `osm-pipeline`: Data processing orchestration
- `osm-2025-poster-incf`: Visualization and reporting

## Current Work (reboot2026_agt branch)

This branch aims to harmonize dsst-etl with work in the related repositories above. See `docs/TODO-reboot2026.md` for the current task list.

## Important Context

- The project uses CC0 license (public domain)
- PDF filenames are often PMIDs (PubMed IDs)
- ODDPub analyzes PDFs for data sharing statements
- Terraform uses OpenTofu (open-source Terraform fork)
- HPC work targets NIH Biowulf/Helix systems

## Common Tasks

### Adding a new database table
1. Add model to `dsst_etl/models.py`
2. Generate migration: `alembic revision --autogenerate -m "description"`
3. Review and apply: `alembic upgrade head`

### Running ODDPub analysis
1. Start services: `docker compose up -d`
2. Use OddpubWrapper class or API at `http://localhost:8071`

### Uploading PDFs to S3
1. Set `S3_BUCKET_NAME` in `.env`
2. Use `dsst_etl.upload_pdfs.upload_directory()`

## Contact

- Project Lead: Adam Thomas (agt24)
- Tech Lead: John Lee (leej3)
- Repository: nimh-dsst/dsst-etl
