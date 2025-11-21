from aws_cdk import (
    Stack,
    CfnOutput,
    aws_glue as glue,
    aws_iam as iam,
    Duration
)
from constructs import Construct
from aws_cdk.aws_s3 import Bucket
from decouple import config

class CatalogStack(Stack):
    """
    AWS Glue Catalog Stack for MPS Project.
    
    Creates a Glue Database and Crawler to automatically catalog data in S3 using Hive partitioning.
    The crawler scans S3 for Parquet files and updates the Data Catalog with schema information.
    
    Attributes:
        data_catalog_db: AWS Glue Database for metadata
        data_crawler: AWS Glue Crawler for schema detection
    """

    def __init__(self, scope: Construct, construct_id: str, data_bucket: Bucket, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Validate input
        if not isinstance(data_bucket, Bucket):
            raise TypeError("data_bucket must be an aws_s3.Bucket instance")

        # Load configuration
        filepath_base_storage = "raw/users"
        crawler_schedule_expression = "cron(0 */2 * * ? *)" # Crawler runs every 2 hours

        # 1. Create Glue Database
        self.data_catalog_db = glue.CfnDatabase(
            self, 
            id="MPS-DataLakeDatabase",
            catalog_id=self.account,
            database_input=glue.CfnDatabase.DatabaseInputProperty(
                name="mps-data-db",
                description="Database to store metadata of users from the Random User API"
            )
        )
        
        # 2. Create IAM Role for Crawler
        crawler_role = iam.Role(
            self, 
            id="MPS-GlueCrawlerRole",
            assumed_by=iam.ServicePrincipal("glue.amazonaws.com"),
            description="Role for Glue Crawler to access S3 and Glue Catalog",
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSGlueServiceRole") 
            ]
        )
        
        # Grant S3 read permissions
        data_bucket.grant_read(crawler_role)
        crawler_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "glue:UpdateDatabase",
                    "glue:UpdateTable",
                    "glue:UpdatePartition",
                    "glue:CreateTable",
                    "glue:CreatePartition",
                    "glue:DeleteTable",
                    "glue:BatchCreatePartition",
                    "glue:BatchDeletePartition",
                    "glue:BatchUpdatePartition"
                ],
                resources=[
                    f"arn:aws:glue:{self.region}:{self.account}:database/{self.data_catalog_db.ref}",
                    f"arn:aws:glue:{self.region}:{self.account}:table/{self.data_catalog_db.ref}/*",
                    f"arn:aws:glue:{self.region}:{self.account}:catalog"
                ]
            )
        )
        
        # Grant Lake Formation permissions (required for table creation with Lake Formation enabled)
        crawler_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "lakeformation:GetDataAccess",
                    "lakeformation:GrantPermissions",
                    "lakeformation:GetResourceLFTags",
                    "lakeformation:ListResources"
                ],
                resources=["*"]
            )
        )
        
        # Grant S3 permissions for Lake Formation data location access
        data_bucket.grant_read_write(crawler_role)

        # 3. Create Glue Crawler
        self.data_crawler = glue.CfnCrawler(
            self, 
            id="MPS-UserDataCrawler",
            name="mps-user-data-crawler",
            role=crawler_role.role_arn,
            database_name=self.data_catalog_db.ref,
            targets=glue.CfnCrawler.TargetsProperty(
                s3_targets=[
                    glue.CfnCrawler.S3TargetProperty(
                        path=f"s3://{data_bucket.bucket_name}/{filepath_base_storage}/",
                        # Exclude partitions metadata files
                        exclusions=["**.json", "**.yaml", "**.txt"]
                    )
                ]
            ),
            schema_change_policy=glue.CfnCrawler.SchemaChangePolicyProperty(
                delete_behavior="DEPRECATE_IN_DATABASE",
                update_behavior="UPDATE_IN_DATABASE"
            ),
            # Crawler configuration
            description="Crawler for scanning Hive-partitioned Parquet files from Random User API",
            schedule=glue.CfnCrawler.ScheduleProperty(
                schedule_expression=crawler_schedule_expression
            ),
            # SchemaChangePolicy detects new columns automatically
            table_prefix="user_",
        )

        # Export outputs
        CfnOutput(
            self, 
            id="GlueDatabaseNameOutput",
            value=self.data_catalog_db.ref,
            description="Name of the Glue Database",
            export_name="mps-glue-database-name"
        )

        CfnOutput(
            self, 
            id="GlueCrawlerNameOutput",
            value=self.data_crawler.name or self.data_crawler.ref,
            description="Name of the Glue Crawler",
            export_name="mps-glue-crawler-name"
        )