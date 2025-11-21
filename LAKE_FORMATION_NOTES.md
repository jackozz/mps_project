# AWS Lake Formation - Config guide

--
After the deployment, we need to add permissions to Glue BD using the web console.

1. Access to **AWS Lake Formation** and check region (`us-east-1`)
2. Access to **Data lake locations** and register new location
    - Select S3 URI
    - Select IAM role
    - Permission mode: can be "Hybrid mode" or "Lake formation", depend of the project permissions structure. I'm using "Hybrid"
3. Access to **Administrative roles and tasks** and add `Manager Administrator` to grant full permissions (catalog creators and database creators)
    - Add IAM project user (for example: `jaime_cruz`)
    - Add IAM Crawler role (for example: `AWSServiceRoleForLakeFormationDataAccess`)
4. Add permissions to crawler. Access to **Data Permissions**
    - Click in **Grant**
    - Select the Crawler Role in `IAM users and roles`
    - Select `Named data catalog resources` and select the `catalog` and `database` to grant permissions
    - Select `Describe`, `Create Table`, `Alter`, `Drop`
    - The `Grantable permissions` section is not necesary.
5. Check the Crawler
    - Ensure that `S3` contains information to process
    - Access to **AWS Glue** - **Data catalog** - **Crawlers**
    - Find `mps-user-data-crawler`. Select it and click on `Run`
    - Wait to end proccess. The "last run" status will be "Succeeded"
6 If the Crawler ends correctly, ✅ **The config is ready**.
    - In **AWS Glue** Access to **Data catalog - Databases - Tables** and check that exists records with table names and contains a valid schema.

---
## Common Troubleshooting

### ❌ Error: "User does not have permission to assume role"
**Solution:**
- Ensure you are a Lake Formation administrator
- Go to Step 2 and verify that your user is listed

### ❌ Error: "Location is already registered"
**Solution:**
- The bucket is already registered in Lake Formation
- Go to Data Lake Locations and verify

### ❌ Crawler fails with permission error
**Solution:**
1. Go to Step 4 and review the permissions
2. Ensure the Crawler role has permissions on the database
3. Try running the Crawler again

### ❌ Cannot register the location (AWSServiceRoleForLakeFormation role does not appear)

**Solution:**
1. Go to **IAM** → **Roles**
2. Search and create if necessary: `AWSServiceRoleForLakeFormation`
3. Return to Lake Formation and try again

### ❌ Crawler creates the table but with incorrect columns

**Solution:**
- Verify that your Parquet file has the correct data types
- Example: `location.postcode` is `int64`

---

## Docs and guides
- [Official AWS Lake formation docs](https://docs.aws.amazon.com/lake-formation/latest/userguide/what-is-lake-formation.html)
- [Setting up Lake Formation](https://docs.aws.amazon.com/lake-formation/latest/userguide/getting-started.html)
- [Granting permissions](https://docs.aws.amazon.com/lake-formation/latest/userguide/granting-permissions.html)
