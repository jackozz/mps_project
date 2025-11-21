# MPS Project
This file contains relevant information about how develop and deploy AWS datalake solution.

## **Requirements information**
- Node.js: v24.11.1 (LTS)
- Python: v3.11.14
- Docker desktop (to check differences between project and AWS cloud)

## **Phase 1: Setup & CDK**
- AWS Regiom: `us-east-1`
- Ppal stack name: `MPS-ProjectStack`

## **Phase 2: Lambda + Random User API**
- Focused in `result` data array from [web randomuser](https://randomuser.me/api/)
- Ingest stack name: `MPS-IngestionStack`

## **Phase 3: S3 + Parquet**
- Storage stack name: `MPS-StorageStack`
- Parquet conversion and ETL Process with Lambda
- Lifecycle transition: 30 days

## **Phase 4: Glue + Lake Formation**
- Catalog stack name: `MPS-CatalogStack`
- Lake Formation roles:
    - mps-users-readonly: `gender`, `email`, `phone`, `cell`, `name.title`, `name.first`, `name.last`
    - mps-analyst-readonly: All columns except `login` section
    - mps-datacientist-readonly: All columns
## **Phase 5: Athena**
- 