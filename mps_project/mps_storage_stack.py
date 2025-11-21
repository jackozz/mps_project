from aws_cdk import (
    RemovalPolicy,
    Stack,
    CfnOutput,
    Duration,
    aws_s3 as s3,
)
from constructs import Construct


class StorageStack(Stack):
    """
    Storage Stack: Creates and configures S3 buckets for the MPS Data Lake
    
    Resources created:
    - data_bucket: Main data lake bucket (Parquet files with Hive partitioning)
    - athena_results_bucket: Query results and temporary data for Athena
    
    Security features:
    - S3-managed encryption on all buckets
    - All public access blocked
    - Server access logging enabled
    - Lifecycle policies for cost optimization
    """

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Common security configuration for all buckets
        common_bucket_config = {
            "encryption": s3.BucketEncryption.S3_MANAGED,
            "block_public_access": s3.BlockPublicAccess.BLOCK_ALL,
            "server_access_logs_prefix": "logs/",
            "removal_policy": RemovalPolicy.DESTROY,  # DESTROY for dev/test, RETAIN for production
        }

        # Lifecycle rules for buckets
        lifecycle_config = {
            "data_lake": [
                s3.LifecycleRule(
                    noncurrent_version_expiration=Duration.days(90),
                    transitions=[
                        s3.Transition(
                            transition_after=Duration.days(30),
                            storage_class=s3.StorageClass.INFREQUENT_ACCESS,
                        ),
                    ],
                )
            ],
            "athena_results": [
                s3.LifecycleRule(
                    noncurrent_version_expiration=Duration.days(5),
                    transitions=[
                        s3.Transition(
                            transition_after=Duration.days(30),
                            storage_class=s3.StorageClass.INFREQUENT_ACCESS,
                        ),
                    ],
                )
            ],
        }

        bucket_names = {
            "data_lake": "MPS-DataLakeBucket",
            "athena_results": "MPS-AthenaQueryResultsBucket",
        }

        # Create main Data Lake bucket
        self.data_bucket = s3.Bucket(
            self,
            id=bucket_names["data_lake"],
            bucket_name=None,  # CDK generates globally unique name
            versioned=True,  # Enable versioning for data lake integrity
            auto_delete_objects=True,  # Allow CDK to delete bucket with versions during stack destruction
            lifecycle_rules=lifecycle_config["data_lake"],
            **common_bucket_config,
        )

        # Create Athena query results bucket
        # Temporary data from Athena queries (no versioning needed)
        self.athena_results_bucket = s3.Bucket(
            self,
            id=bucket_names["athena_results"],
            bucket_name=None,  # CDK generates globally unique name
            versioned=False,  # Temporary data, no version history needed
            auto_delete_objects=True,  # Allow CDK to delete bucket during stack destruction
            lifecycle_rules=lifecycle_config["athena_results"],
            **common_bucket_config,
        )

        # Export bucket information for other stacks and external consumption
        CfnOutput(
            self,
            "DataBucketName",
            value=self.data_bucket.bucket_name,
            description="S3 bucket for data lake (Parquet files)",
            export_name="MPS-DataBucketName",
        )
        CfnOutput(
            self,
            "DataBucketArn",
            value=self.data_bucket.bucket_arn,
            description="ARN of the data lake bucket",
            export_name="MPS-DataBucketArn",
        )
        CfnOutput(
            self,
            "AthenaResultsBucketName",
            value=self.athena_results_bucket.bucket_name,
            description="S3 bucket for Athena query results",
            export_name="MPS-AthenaResultsBucketName",
        )
        CfnOutput(
            self,
            "AthenaResultsBucketArn",
            value=self.athena_results_bucket.bucket_arn,
            description="ARN of the Athena results bucket",
            export_name="MPS-AthenaResultsBucketArn",
        )
