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
- Parquet conversion and ETL Process

## **Phase 3: S3 + Parquet**
- Storage stack name: `MPS-StorageStack`
- Datalake bucket name: `MPS-DataLakeBucket`    
    - Versioned: True
    - Lifecycle transition: 30 days
- Athena results bucket name: `MPS-AthenaQueryResultsBucket`
    - Versioned: False
    - Lifecycle transition: 1 days

## **Phase 4: Glue + Lake Formation**
- Catalog stack name: `MPS-CatalogStack`
- AWS Glue table name: `user_users`
- Permissions stack name: `MPS-PermissionsStack`
- Lake Formation roles (Created via CDK, configured in AWS Web Console):
    - **mps-users-readonly**: Can view email, phone, cell, name.title, name.first, name.last (6 columns)
    - **mps-analyst-readonly**: Can view all columns except login section (26 columns)
    - **mps-datacientist-readonly**: Can view all columns (33 columns)

### Column permision Matrix - Table `mps_users`

| Rol | Total Columns | Data Contact Columns | Data Demographic Columns | Data Security Columns |
|-----|:--------------:|:-------------------:|:------------------:|:------------------:|
| **mps-users-readonly** | 6 | ✅ (6) | ❌ | ❌ |
| **mps-analyst-readonly** | 26 | ✅ (6) | ✅ (20) | ❌ |
| **mps-datacientist-readonly** | 33 | ✅ (6) | ✅ (20) | ✅ (7) |

## Detailed permissions

| Column | mps-users-readonly | mps-analyst-readonly | mps-datacientist-readonly |
|---------|:------------------:|:--------------------:|:-------------------------:|
| gender | ❌ | ✅ | ✅ |
| email | ✅ | ✅ | ✅ |
| phone | ✅ | ✅ | ✅ |
| cell | ✅ | ✅ | ✅ |
| nat | ❌ | ✅ | ✅ |
| name.title | ✅ | ✅ | ✅ |
| name.first | ✅ | ✅ | ✅ |
| name.last | ✅ | ✅ | ✅ |
| location.street.number | ❌ | ✅ | ✅ |
| location.street.name | ❌ | ✅ | ✅ |
| location.city | ❌ | ✅ | ✅ |
| location.state | ❌ | ✅ | ✅ |
| location.country | ❌ | ✅ | ✅ |
| location.postcode | ❌ | ✅ | ✅ |
| location.coordinates.latitude | ❌ | ✅ | ✅ |
| location.coordinates.longitude | ❌ | ✅ | ✅ |
| location.timezone.offset | ❌ | ✅ | ✅ |
| location.timezone.description | ❌ | ✅ | ✅ |
| login.uuid | ❌ | ❌ | ✅ |
| login.username | ❌ | ❌ | ✅ |
| login.password | ❌ | ❌ | ✅ |
| login.salt | ❌ | ❌ | ✅ |
| login.md5 | ❌ | ❌ | ✅ |
| login.sha1 | ❌ | ❌ | ✅ |
| login.sha256 | ❌ | ❌ | ✅ |
| dob.date | ❌ | ✅ | ✅ |
| dob.age | ❌ | ✅ | ✅ |
| registered.date | ❌ | ✅ | ✅ |
| registered.age | ❌ | ✅ | ✅ |
| id.name | ❌ | ✅ | ✅ |
| id.value | ❌ | ✅ | ✅ |
| picture.large | ❌ | ✅ | ✅ |
| picture.medium | ❌ | ✅ | ✅ |
| picture.thumbnail | ❌ | ✅ | ✅ |
| year | ❌ | ✅ | ✅ |
| month | ❌ | ✅ | ✅ |
| day | ❌ | ✅ | ✅ |

## **Phase 5: Athena**
- Athena query test:
```sql
SELECT
    email
FROM mps.users
GROUP BY 1, 2
LIMIT 10;
```
