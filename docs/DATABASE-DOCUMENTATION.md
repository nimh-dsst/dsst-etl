# DSST-ETL Database Documentation

**Document Created:** 2025-12-22
**Database Snapshot Date:** 2025-12-22 (data last loaded: 2025-02-13)
**Database Server:** AWS RDS PostgreSQL 15.10
**Instance:** See `POSTGRES_HOST` in repository secrets or `.env` file

---

## Overview

The DSST-ETL project uses two PostgreSQL databases on the same RDS instance:

| Database | Purpose | Status |
|----------|---------|--------|
| `dsst_etl` | Production database (empty schema) | Schema only, no data |
| `pdx` | Development/working database | Active with 759 records |

---

## Database: `pdx` (Primary Working Database)

### Summary Statistics

| Table | Record Count |
|-------|--------------|
| alembic_version | 1 |
| documents | 759 |
| identifier | 759 |
| oddpub_metrics | 759 |
| provenance | 1 |
| rtransparent_publication | 0 |
| works | 759 |

**Data Load Date:** 2025-02-13 16:20 - 17:49 UTC
**PMID Range:** 12858133 - 33600085

### ODDPub Analysis Summary

| Metric | Count |
|--------|-------|
| Publications with open data | 0 |
| Publications with open code | 0 |
| Publications with data availability statement | 0 |

---

## Table Schemas

### 1. alembic_version

Tracks database migration state.

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| version_num | varchar | NO | Current migration version |

**Record Count:** 1

**Example Record:**
```
version_num: ea94fafc9590
```

---

### 2. documents

Stores metadata for uploaded PDF documents.

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| id | integer | NO | Primary key (auto-increment) |
| hash_data | varchar | NO | SHA hash of PDF file content |
| created_at | timestamp | YES | Upload timestamp |
| s3uri | text | NO | S3 location of the PDF |
| provenance_id | integer | YES | FK to provenance table |

**Record Count:** 759

**Example Records:**
```
Record 1:
  id: 1
  hash_data: 84568aeb96bc7119f551cc28e4de6cbc7f76a6de8ea7045040c4579f8...
  created_at: 2025-02-13 16:20:27.648733
  s3uri: s3://${S3_BUCKET_NAME}/new-folder//12858133.pdf
  provenance_id: 1

Record 2:
  id: 2
  hash_data: cee76f09424bdb120ebcbc8c07a3779b7bc881c33539008a798f75b3d...
  created_at: 2025-02-13 16:20:36.239874
  s3uri: s3://${S3_BUCKET_NAME}/new-folder//15240348.pdf
  provenance_id: 1

Record 3:
  id: 3
  hash_data: ed283ee3e4fa6b113f70cdd08b4469e6deb8f30a82164790a0c86afb7...
  created_at: 2025-02-13 16:20:41.298143
  s3uri: s3://${S3_BUCKET_NAME}/new-folder//15684031.pdf
  provenance_id: 1
```

---

### 3. identifier

Maps publication identifiers (PMID, PMCID, DOI) to documents.

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| core_id | integer | NO | Primary key (auto-increment) |
| pmid | integer | YES | PubMed ID |
| pmcid | varchar | YES | PubMed Central ID |
| doi | varchar | YES | Digital Object Identifier |
| document_id | integer | NO | FK to documents table |
| provenance_id | integer | NO | FK to provenance table |
| created_at | timestamp | YES | Creation timestamp |

**Record Count:** 759

**Example Records:**
```
Record 1:
  core_id: 1
  pmid: 12858133
  pmcid: None
  doi: None
  document_id: 1
  provenance_id: 1
  created_at: 2025-02-13 16:20:27.648733

Record 2:
  core_id: 2
  pmid: 15240348
  pmcid: None
  doi: None
  document_id: 2
  provenance_id: 1
  created_at: 2025-02-13 16:20:36.239874

Record 3:
  core_id: 3
  pmid: 15684031
  pmcid: None
  doi: None
  document_id: 3
  provenance_id: 1
  created_at: 2025-02-13 16:20:41.298143
```

---

### 4. oddpub_metrics

Stores open data/code detection results from ODDPub analysis.

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| id | integer | NO | Primary key (auto-increment) |
| article | varchar | YES | Article filename |
| is_open_data | boolean | YES | Has open data statement |
| open_data_category | varchar | YES | Category of open data |
| is_reuse | boolean | YES | Data is reusable |
| is_open_code | boolean | YES | Has open code statement |
| is_open_data_das | boolean | YES | Has data availability statement |
| is_open_code_cas | boolean | YES | Has code availability statement |
| das | varchar | YES | Data availability statement text |
| open_data_statements | varchar | YES | Open data statement text |
| cas | varchar | YES | Code availability statement text |
| open_code_statements | varchar | YES | Open code statement text |
| work_id | integer | YES | FK to works table |
| provenance_id | integer | YES | FK to provenance table |
| document_id | integer | YES | FK to documents table |

**Record Count:** 759

**Example Records:**
```
Record 1:
  id: 1
  article: 34626164.txt
  is_open_data: False
  open_data_category: (empty)
  is_reuse: False
  is_open_code: False
  is_open_data_das: False
  is_open_code_cas: False
  das: None
  open_data_statements: (empty)
  cas: None
  open_code_statements: (empty)
  work_id: 1
  provenance_id: 1
  document_id: 1
```

---

### 5. provenance

Audit trail for data operations and pipeline runs.

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| id | integer | NO | Primary key (auto-increment) |
| pipeline_name | varchar | YES | Name of the pipeline/process |
| version | varchar | YES | Software version |
| compute | text | YES | Compute environment identifier |
| personnel | text | YES | Username/hostname |
| comment | text | YES | Description of the operation |

**Record Count:** 1

**Example Record:**
```
Record 1:
  id: 1
  pipeline_name: PMID Inventory and Oddpub Analysis
  version: 0.1.dev163+gd4829da.d20250212
  compute: 2446355096732914821
  personnel: localhost
  comment: Creating document inventory of PDFs where the title is th...
```

---

### 6. rtransparent_publication

Stores comprehensive publication metrics from RTransparent analysis.

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| id | integer | NO | Primary key |
| title | varchar | YES | Publication title |
| author | varchar | YES | Author(s) |
| is_open_code | boolean | YES | Has open code |
| is_open_data | boolean | YES | Has open data |
| year | integer | YES | Publication year |
| filename | varchar | YES | Source filename |
| pmcid_pmc | integer | YES | PMC ID |
| pmid | integer | YES | PubMed ID |
| doi | varchar | YES | DOI |
| journal | varchar | YES | Journal name |
| publisher | varchar | YES | Publisher |
| ... | ... | ... | (150+ additional columns for detailed metrics) |
| work_id | integer | YES | FK to works table |
| provenance_id | integer | YES | FK to provenance table |

**Record Count:** 0 (schema only, no data loaded)

---

### 7. works

Represents distinct academic publications (may have multiple documents).

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| id | integer | NO | Primary key (auto-increment) |
| created_at | timestamp | YES | Creation timestamp |
| modified_at | timestamp | YES | Last modification timestamp |
| initial_document_id | integer | YES | FK to first document |
| primary_document_id | integer | YES | FK to canonical document |
| provenance_id | integer | YES | FK to provenance table |

**Record Count:** 759

**Example Records:**
```
Record 1:
  id: 1
  created_at: 2025-02-13 16:20:27.648733
  modified_at: 2025-02-13 16:20:27.648733
  initial_document_id: 1
  primary_document_id: 1
  provenance_id: 1

Record 2:
  id: 2
  created_at: 2025-02-13 16:20:36.239874
  modified_at: 2025-02-13 16:20:36.239874
  initial_document_id: 2
  primary_document_id: 2
  provenance_id: 1

Record 3:
  id: 3
  created_at: 2025-02-13 16:20:41.298143
  modified_at: 2025-02-13 16:20:41.298143
  initial_document_id: 3
  primary_document_id: 3
  provenance_id: 1
```

---

## Entity Relationship Diagram

```
┌─────────────────┐       ┌─────────────────┐
│   provenance    │       │     works       │
├─────────────────┤       ├─────────────────┤
│ id (PK)         │◄──────│ provenance_id   │
│ pipeline_name   │       │ id (PK)         │
│ version         │       │ created_at      │
│ compute         │       │ modified_at     │
│ personnel       │       │ initial_doc_id  │──┐
│ comment         │       │ primary_doc_id  │──┤
└────────┬────────┘       └────────┬────────┘  │
         │                         │           │
         │    ┌────────────────────┘           │
         │    │                                │
         ▼    ▼                                ▼
┌─────────────────┐       ┌─────────────────────┐
│   documents     │◄──────│     identifier      │
├─────────────────┤       ├─────────────────────┤
│ id (PK)         │       │ core_id (PK)        │
│ hash_data       │       │ pmid                │
│ created_at      │       │ pmcid               │
│ s3uri           │       │ doi                 │
│ provenance_id   │       │ document_id (FK)    │
└────────┬────────┘       │ provenance_id (FK)  │
         │                │ created_at          │
         │                └─────────────────────┘
         │
         ▼
┌─────────────────────┐   ┌─────────────────────────────┐
│   oddpub_metrics    │   │  rtransparent_publication   │
├─────────────────────┤   ├─────────────────────────────┤
│ id (PK)             │   │ id (PK)                     │
│ article             │   │ title, author, year...      │
│ is_open_data        │   │ is_open_data, is_open_code  │
│ is_open_code        │   │ (150+ metric columns)       │
│ work_id (FK)        │   │ work_id (FK)                │
│ document_id (FK)    │   │ provenance_id (FK)          │
│ provenance_id (FK)  │   └─────────────────────────────┘
└─────────────────────┘
```

---

## Connection Details

Connection credentials are stored in AWS SSM Parameter Store under the `/dsst-etl/` path.

### Retrieving Secrets (requires MFA)

```bash
# Get MFA session first (replace CODE with your 6-digit MFA code)
aws sts get-session-token \
  --serial-number arn:aws:iam::${AWS_ACCOUNT_ID}:mfa/YourMFADevice \
  --token-code CODE \
  --profile nimh-irp

# Export the returned credentials, then retrieve parameters:
aws ssm get-parameters-by-path --path "/dsst-etl/" --with-decryption \
  --query 'Parameters[*].[Name,Value]' --output table
```

### Required environment variables (from SSM)
- `POSTGRES_HOST` - Database endpoint (`/dsst-etl/POSTGRES_HOST`)
- `POSTGRES_PASSWORD` - Database password (`/dsst-etl/POSTGRES_PASSWORD`)
- `POSTGRES_DB` - Database name (`/dsst-etl/POSTGRES_DB`)

```bash
# Connection string format
postgresql://postgres:${POSTGRES_PASSWORD}@${POSTGRES_HOST}:5432/${POSTGRES_DB}

# Using psql
PGPASSWORD=$POSTGRES_PASSWORD psql -h $POSTGRES_HOST -U postgres -d $POSTGRES_DB

# Using Python
import os
import psycopg2
conn = psycopg2.connect(
    host=os.environ['POSTGRES_HOST'],
    port=5432,
    dbname=os.environ.get('POSTGRES_DB', 'pdx'),
    user='postgres',
    password=os.environ['POSTGRES_PASSWORD']
)
```

---

## Notes

1. **Two databases exist**: `dsst_etl` (empty) and `pdx` (with data). The `pdx` database is the active working database.

2. **Identifier coverage**: Currently only PMIDs are populated; PMCID and DOI fields are null for all records.

3. **ODDPub results**: All 759 analyzed publications show no open data or open code detected. This may indicate:
   - The analysis pipeline needs refinement
   - The sample publications don't contain open data/code statements
   - The ODDPub service configuration needs adjustment

4. **RTransparent table**: Schema exists with 150+ columns but no data has been loaded yet.

5. **Single provenance record**: All 759 documents/works reference the same provenance entry, indicating they were uploaded in a single batch operation on 2025-02-13.
