# DSST-ETL Repository: Goals and Progress Report

**Document Created:** 2025-12-22
**Period Covered:** October 2023 - January 2025
**Data Sources:** Git commits, GitHub Issues, GitHub Pull Requests (as of 2025-12-22)

---

## Executive Summary

The DSST-ETL (Data Science and Sharing Team - Extract Transform Load) repository is an NIMH initiative focused on building infrastructure for extracting, processing, and managing scientific publication data. Since its inception in October 2023, the project has evolved from initial data gathering scripts into a comprehensive database-backed ETL pipeline with containerized services for PDF analysis.

---

## Project Goals

### Primary Objectives

1. **Publication Data Collection**: Scrape and aggregate publication data from NIH intramural research programs, including PMIDs, DOIs, and principal investigator information
2. **PDF Document Management**: Upload, store, and track scientific publication PDFs in S3 with database provenance tracking
3. **Open Science Metrics Analysis**: Integrate tools like ODDPub to analyze publications for data sharing statements and open science practices
4. **Database Infrastructure**: Build a robust PostgreSQL database with proper schema design, migrations, and cloud deployment
5. **Reproducible Pipelines**: Create containerized, testable, and deployable ETL workflows

---

## Branch Overview

The repository maintains **5 branches**, each serving distinct purposes:

### 1. `main` (Primary Development Branch)
- **Status**: Active, production-ready code
- **Commits since Oct 2023**: 80+
- **Purpose**: Contains merged, reviewed code ready for deployment
- **Key Contents**: Core ETL package, database models, Docker configurations, CI/CD workflows

### 2. `irp-pdf` (IRP PDF Inventory Processing)
- **Status**: Active development
- **Commits since Oct 2023**: 100+
- **Purpose**: Processing PDF inventories where filenames are PMIDs
- **Key Features**:
  - S3 bucket inventory processing
  - Batch PDF processing with ODDPub integration
  - Alembic migration improvements
  - Apptainer/Singularity definitions for HPC deployment
  - Minio integration for local S3 emulation testing

### 3. `nimh2023report` (NIMH 2023 Report Data)
- **Status**: Historical/Archive
- **Commits**: 12
- **Purpose**: Contains data and scripts used for the NIMH 2023 annual report
- **Key Contents**:
  - Publication data extraction pipelines
  - RTransparent output data
  - OpenAlex open access URL data
  - ShareStats panel data

### 4. `olmocr` (Visual Language Model OCR)
- **Status**: Active development (feature branch)
- **Commits**: Extends main branch
- **Purpose**: Same as main (preparing for olmOCR integration)
- **Future Work**: Integration of AllenAI's olmOCR for PDF-to-text conversion

### 5. `parallel` (Parallelization Development)
- **Status**: Active development
- **Commits**: Extends main branch
- **Purpose**: Parallelization of PDF inventory processing for HPC environments (Biowulf/Helix)

---

## Timeline of Progress

### Phase 1: Foundation (October 2023 - January 2024)

**October 2023**
- **Initial commit** by leo_rsnd (Oct 12, 2023)
- Repository created for NIMH 2023 report data processing
- Initial publication data pipelines established

**January-February 2024**
- RTransparent output processing
- OpenAlex integration for open access URLs
- Journal and title data from PubMed
- ShareStats panel code and data
- Data documentation

### Phase 2: Script Modernization (October 2024)

**October 2024** - Major development push by Joshua Lawrimore
- Fixed `get_pmids.py` to work with updated NIH Annual Research Report webpage structure
- Wrote `annual_parser.py` module for IC access
- Added retry logic for PubMed eutils API (10 retries to handle 400 errors)
- Fixed multi-PI parsing bug in project pages
- Updated dependencies and requirements documentation

**Issues Resolved:**
- Issue #1: Multi-IC parsing in get_ipids.py (CLOSED)
- Issue #2: Requirements file creation (CLOSED)
- Issue #3: Multi-PI project page parsing (CLOSED)
- Issue #4: Testing with new scraped data (CLOSED)
- Issue #5: 400 Bad Request errors in PubMed API (CLOSED)

### Phase 3: Database Infrastructure (November 2024)

**November 2024** - Major infrastructure development

**Key Accomplishments:**
- **Project reorganization**: Switch to `uv` package management
- **Docker Compose setup**: Local PostgreSQL deployment
- **Database schema design**: Documents, Works, Provenance tables using SQLAlchemy
- **Alembic migrations**: Version-controlled database schema
- **S3 integration**: PDF upload to AWS S3 with hash-based deduplication
- **CI/CD**: GitHub Actions for automated testing
- **Pre-commit hooks**: Code quality enforcement

**Pull Requests:**
- PR #7: Database Development (MERGED Nov 19)
- PR #8: Dev 2024 branch merge (MERGED Nov 18)
- PR #9: Generate work for document (MERGED Nov 25)
- PR #11: HHS DOI CLI tool (MERGED Dec 2)

**Issues Resolved:**
- Issue #6: Database Development - comprehensive schema creation (CLOSED)

### Phase 4: Analysis Tool Integration (December 2024)

**December 2024** - ODDPub and RTransparent integration

**Key Accomplishments:**
- **RTransparent Publication schema**: Database table for publication metrics
- **ODDPub Docker service**: FastAPI wrapper for R-based ODDPub analysis
- **OddpubMetrics table**: Database schema for open data detection metrics
- **OddpubWrapper class**: Python interface for PDF processing and API integration
- **Comprehensive testing**: Unit tests with database rollback

**Pull Requests:**
- PR #12: RTransparent Publication Ingestion (MERGED Dec 9)
- PR #14: OddpubMetrics Docker image (CLOSED - superseded)
- PR #15: OddpubMetrics Docker image and Database Table Generation (MERGED Jan 3)

**Issues Resolved:**
- Issue #10: RTransparent Publication Ingestion (CLOSED Dec 9)
- Issue #13: OddpubMetrics Docker image and Database Table Generation (CLOSED Jan 9)

### Phase 5: Production Deployment (January 2025)

**January 2025** - AWS deployment and identifier management

**Key Accomplishments:**
- **Identifier Table**: PMID, PMCID, DOI tracking with document relationships
- **AWS RDS deployment**: Terraform/OpenTofu configuration for PostgreSQL
- **CC0 License**: Project licensed under Creative Commons Zero
- **README improvements**: Developer setup documentation
- **S3 PDF inventory**: 3,538+ PDFs uploaded to S3 bucket (see SSM `/dsst-etl/S3_BUCKET_NAME`)

**Pull Requests:**
- PR #17: AWS RDS configuration with PostgreSQL (MERGED Jan 20)
- PR #19: Identifier Table (MERGED Jan 9)
- PR #20: LICENSE.md creation (MERGED Dec 24)
- PR #24: README tidy (MERGED Jan 28)

**Issues Resolved:**
- Issue #16: Identifier Table (CLOSED Jan 9)
- Issue #18: Project needs license (CLOSED Jan 6)

### Phase 6: Scale-up and HPC Integration (February 2025 - Present)

**Current Development Focus:**
- PDF inventory processing at scale
- Apptainer/Singularity definitions for Biowulf HPC
- Podman Compose support
- Minio S3 emulation for local testing

---

## Issues Summary

### Closed Issues (11 total)

| # | Title | Opened | Closed | Summary |
|---|-------|--------|--------|---------|
| 1 | get_ipids.py NIMH-only parsing | Oct 7, 2024 | Oct 9, 2024 | Fixed multi-IC support |
| 2 | No requirements file | Oct 7, 2024 | Oct 9, 2024 | Added dependencies |
| 3 | Multi-PI project page parsing | Oct 9, 2024 | Oct 9, 2024 | Fixed PI name extraction |
| 4 | Test new scraped data | Oct 10, 2024 | Oct 10, 2024 | Validated with retry logic |
| 5 | 400 Bad Request errors | Oct 10, 2024 | Oct 10, 2024 | Added retry mechanism |
| 6 | Database Development | Nov 8, 2024 | Nov 25, 2024 | Full schema implementation |
| 10 | RTransparent Publication Ingestion | Nov 25, 2024 | Dec 9, 2024 | Metrics table and upload |
| 13 | OddpubMetrics Docker | Dec 5, 2024 | Jan 9, 2025 | Docker service + DB table |
| 16 | Identifier Table | Dec 17, 2024 | Jan 9, 2025 | PMID/DOI/PMCID tracking |
| 18 | Project needs license | Dec 23, 2024 | Jan 6, 2025 | CC0 license added |

### Open Issues (4 total)

| # | Title | Opened | Status | Description |
|---|-------|--------|--------|-------------|
| 22 | PDF Inventory where title is PMID | Jan 9, 2025 | Active | Processing 3,538 PDFs from IRP |
| 23 | PDF Inventory where title is not PMID | Jan 9, 2025 | Pending | PDFs without PMID filenames |
| 25 | Parallelization of pmid inventory code | Feb 13, 2025 | Active | HPC/Biowulf parallel processing |
| 26 | olmOCR Integration | May 22, 2025 | Planned | Visual Language Model OCR |

---

## Pull Requests Summary

### Merged PRs (10 total)

| # | Title | Author | Merged | Key Changes |
|---|-------|--------|--------|-------------|
| 7 | Database Development | quang-ng | Nov 19, 2024 | Core DB schema, S3 integration |
| 8 | Dev 2024 | joshlawrimore | Nov 18, 2024 | Branch consolidation |
| 9 | Generate work for document | quang-ng | Nov 25, 2024 | PDF upload enhancements |
| 11 | HHS DOI CLI | joshlawrimore | Dec 2, 2024 | PDF filtering tool |
| 12 | RTransparent Publication Ingestion | quang-ng | Dec 9, 2024 | Publication metrics |
| 15 | OddpubMetrics Docker | quang-ng | Jan 3, 2025 | ODDPub service + tables |
| 17 | AWS RDS configuration | quang-ng | Jan 20, 2025 | Terraform PostgreSQL |
| 19 | Identifier Table | quang-ng | Jan 9, 2025 | PMID/DOI/PMCID schema |
| 20 | Create LICENSE.md | quang-ng | Dec 24, 2024 | CC0 license |
| 24 | tidy readme | leej3 | Jan 28, 2025 | Documentation improvements |

### Open PRs (1 total)

| # | Title | Author | Status | Description |
|---|-------|--------|--------|-------------|
| 21 | PDF Inventory where title is PMID | quang-ng | In Review | S3 inventory processing, ODDPub integration |

---

## Key Contributors

| Contributor | GitHub | Role | Key Contributions |
|-------------|--------|------|-------------------|
| Joshua Lawrimore | joshlawrimore | Lead Developer | Script modernization, data scraping, testing |
| Quang Nguyen | quang-ng | Developer | Database infrastructure, Docker services, API integration |
| John Lee | leej3 | Tech Lead | Architecture, code review, CI/CD, AWS deployment |
| Adam Thomas | agt24 | Project Lead | Project direction, requirements, license decisions |
| leo_rsnd | leo_rsnd | Initial Developer | Original pipeline and data processing |

---

## Technical Architecture

### Database Schema

```
Documents Table
├── id (auto-generated)
├── hash (PDF file hash)
├── created_at
├── s3uri (S3 storage location)
├── work_id (FK to Works)
└── provenance_id (FK to Provenance)

Works Table
├── id (auto-generated)
├── created_at
├── modified_at
├── initial_document_id (FK to Documents)
├── primary_document_id (FK to Documents)
└── provenance_id (FK to Provenance)

Provenance Table
├── id (auto-generated)
├── pipeline_name
├── version
├── compute
├── personnel
└── comment

Identifier Table
├── core_id (PK)
├── pmid (PubMed ID)
├── pmcid (PubMed Central ID)
├── doi (Digital Object Identifier)
├── document_id (FK to Documents)
├── provenance_id (FK to Provenance)
└── created_at

OddpubMetrics Table
├── article
├── is_open_data
├── is_open_code
├── open_data_statements
├── open_code_statements
└── (additional ODDPub fields)
```

### Infrastructure

- **Package Management**: uv (Python), renv (R)
- **Database**: PostgreSQL (local Docker + AWS RDS)
- **Storage**: AWS S3 (bucket name in SSM Parameter Store)
- **Containerization**: Docker, Docker Compose, Apptainer/Singularity
- **IaC**: OpenTofu/Terraform
- **CI/CD**: GitHub Actions
- **Testing**: pytest with database rollback

---

## Current Status and Future Work

### Completed Milestones
- [x] Publication data scraping pipeline
- [x] Database schema design and implementation
- [x] S3 PDF storage integration
- [x] ODDPub Docker service and metrics collection
- [x] Identifier table for PMID/DOI/PMCID tracking
- [x] AWS RDS deployment
- [x] CC0 licensing
- [x] CI/CD pipeline

### In Progress
- [ ] PDF inventory processing (Issue #22) - 3,538 PDFs
- [ ] Parallel processing for HPC (Issue #25)

### Planned
- [ ] PDF inventory for non-PMID titles (Issue #23)
- [ ] olmOCR integration for PDF-to-text (Issue #26)
- [ ] Identifier conflict resolution
- [ ] Large-scale production deployment

---

## Conclusion

The DSST-ETL repository has made substantial progress since October 2023, transforming from a collection of data scraping scripts into a comprehensive, database-backed ETL infrastructure. Key achievements include:

1. **Robust database design** with proper migrations and provenance tracking
2. **Containerized analysis services** (ODDPub) for open science metrics
3. **Cloud deployment** on AWS with Infrastructure as Code
4. **Scalable architecture** supporting thousands of PDF documents
5. **Strong development practices** including CI/CD, testing, and code review

The project is well-positioned for the next phase of scale-up, with planned parallelization for HPC environments and integration of modern OCR capabilities.

---

*Report generated from repository commit history, issues, and pull requests.*
