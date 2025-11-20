from aws_cdk import (
    RemovalPolicy,
    Stack,
    CfnOutput,
    Duration,
    aws_s3 as s3,
)
from constructs import Construct

class StorageStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create S3 Bucket with improved security and configuration
        # (WARNING!) RemovalPolicy.DESTROY causes the bucket to be DELETED with ALL its contents
        # if you destroy the CDK stack. In production, we use RETAIN.
        # In this lab, we use DESTROY for convenience.
        self.data_bucket = s3.Bucket(
            self, "DataLakeBucket",
            # Use CDK-generated name for global uniqueness
            bucket_name=None,
            # Encryption is always recommended
            encryption=s3.BucketEncryption.S3_MANAGED,
            # Ensure only the account owner has access (Good security practice)
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            # Enable versioning for Data Lakes (recommended)
            versioned=True,
            # Enable server access logging for audit trails
            server_access_logs_prefix="logs/",
            # Use DESTROY for dev/test, RETAIN for production
            removal_policy=RemovalPolicy.DESTROY,
            # Auto-delete old versions after 90 days and transition to cheaper storage
            lifecycle_rules=[
                s3.LifecycleRule(
                    noncurrent_version_expiration=Duration.days(90),
                    transitions=[
                        s3.Transition(
                            transition_after=Duration.days(30),
                            storage_class=s3.StorageClass.INFREQUENT_ACCESS, 
                            # Alternative: INTELLIGENT_TIERING for unpredictable data access 
                            # and automatic cost optimization
                        ),
                    ],
                )
            ],
        )

        # Outputs so we can see the bucket name and ARN after deployment
        # Useful for the next phase and integration with other services
        CfnOutput(self, "DataBucketName", value=self.data_bucket.bucket_name)
        CfnOutput(self, "DataBucketArn", value=self.data_bucket.bucket_arn)