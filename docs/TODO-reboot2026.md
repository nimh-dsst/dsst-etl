# DSST-ETL Reboot 2026 Todo List

**Document Created:** 2025-12-22
**Branch:** `reboot2026_agt`
**Goal:** Harmonize this work with recent work done in related repositories (osm-2025-poster-incf, osm, and osm-pipeline)

---

## Completed Tasks

- [x] Create new branch `reboot2026_agt`
- [x] Create `docs/` folder in the branch
- [x] Rename `PROGRESS_REPORT.md` to `DSST-ETL-REPO-OVERVIEW-2023-TO-JAN-2025.md` and move to `docs/`
- [x] Assess current state of AWS infrastructure
- [x] Store this Todo list in `docs/`
- [x] Create `Claude.md`

---

## AWS Infrastructure Assessment

### Current State (as of December 2024)

#### S3 Buckets
| Bucket Name | Purpose | Status |
|-------------|---------|--------|
| `${S3_BUCKET_NAME}` | PDF document storage | Active - Contains 3,538+ PDFs |
| Terraform state bucket | Terraform state storage | Active |

#### PostgreSQL (RDS)
| Resource | Details |
|----------|---------|
| **Instance Endpoint** | `${POSTGRES_HOST}` |
| **Engine** | PostgreSQL 15.10 |
| **Instance Class** | `db.t3.micro` |
| **Storage** | 20 GB |
| **Database Name** | `${POSTGRES_DB}` |
| **Username** | `postgres` |
| **Region** | `${AWS_REGION}` |
| **Publicly Accessible** | Yes |
| **Backup Retention** | 30 days |
| **Backup Window** | 03:00-04:00 UTC |

#### VPC/Networking
| Resource | Details |
|----------|---------|
| **VPC** | Shared VPC (see terraform configuration) |
| **Subnets** | Two subnets across us-east-1a and us-east-1b |
| **Security Group** | Allows PostgreSQL (5432) access |
| **Subnet Group** | Shared RDS subnet group |

#### EC2 Instances
- **Status:** No EC2 instances currently deployed for this project
- **Note:** Processing is designed to run on local machines or Biowulf HPC

#### Terraform State Management
| Resource | Details |
|----------|---------|
| **State Bucket** | Terraform state bucket (see terraform config) |
| **DynamoDB Lock Table** | State locks table |
| **State Key** | `postgres/terraform.tfstate` |

#### SSM Parameter Store
Secrets are stored in AWS SSM Parameter Store under `/dsst-etl/`:
- `/dsst-etl/POSTGRES_HOST`
- `/dsst-etl/POSTGRES_PASSWORD`
- `/dsst-etl/POSTGRES_DB`
- `/dsst-etl/S3_BUCKET_NAME`

Access requires MFA authentication.

---

## Harmonization Tasks (Pending)

### Phase 1: Repository Alignment
- [ ] Review osm-2025-poster-incf repository structure and patterns
- [ ] Review osm repository current state
- [ ] Review osm-pipeline repository architecture
- [ ] Identify common patterns and conventions across repos
- [ ] Document architectural decisions for harmonization

### Phase 2: Code Consolidation
- [ ] Identify duplicate functionality across repositories
- [ ] Determine canonical location for shared utilities
- [ ] Plan migration strategy for shared components
- [ ] Update import paths and dependencies

### Phase 3: Database Schema Alignment
- [ ] Review database schemas across projects
- [ ] Identify overlapping or conflicting table definitions
- [ ] Plan schema migration/consolidation strategy
- [ ] Update Alembic migrations as needed

### Phase 4: Infrastructure Alignment
- [ ] Review AWS infrastructure across projects
- [ ] Consolidate S3 bucket usage
- [ ] Ensure consistent naming conventions
- [ ] Update Terraform configurations

### Phase 5: Documentation
- [ ] Create unified architecture documentation
- [ ] Update READMEs across repositories
- [ ] Document cross-repository dependencies
- [ ] Create developer onboarding guide

---

## Related Repositories

| Repository | Description | Relationship |
|------------|-------------|--------------|
| `osm-2025-poster-incf` | INCF poster materials | Data visualization and reporting |
| `osm` | Open Science Metrics core | Core metrics calculations |
| `osm-pipeline` | Data processing pipelines | ETL orchestration |
| `dsst-etl` | Extract-Transform-Load infrastructure | Database and storage |

---

## Notes

- AWS Profile for CLI access: `nimh-irp`
- Terraform tool: OpenTofu (open-source Terraform fork)
- Package manager: `uv` (Python), `renv` (R)
- Database migrations: Alembic
- Container runtime: Docker/Podman, Apptainer (for HPC)
