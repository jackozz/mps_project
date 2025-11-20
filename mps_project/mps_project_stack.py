from constructs import Construct
from aws_cdk import (
    Stack,
    CfnOutput,
)
from .mps_ingestion_stack import MpsIngestionStack
from .mps_storage_stack import StorageStack

class MpsProjectStack(Stack):
    """
    Main stack that orchestrates the MPS Project infrastructure.
    
    Components:
    - Storage Stack: S3 bucket for data lake
    - Ingestion Stack: Lambda function for data fetching
    """

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create data storage stack
        self.storage_stack = StorageStack(
            self, "StorageStack",
            stack_name="mps-storage-stack"
        )

        # Create data ingestion stack
        self.ingestion_stack = MpsIngestionStack(
            self, "IngestionStack",
            data_bucket=self.storage_stack.data_bucket,
            stack_name="mps-ingestion-stack"
        )

        # Define explicit dependency
        self.ingestion_stack.add_dependency(self.storage_stack)

        # Grant Lambda write permissions to S3 bucket
        self.storage_stack.data_bucket.grant_write(
            self.ingestion_stack.data_fetcher_lambda.role
        )

        # Export key outputs for external access
        CfnOutput(
            self, "DataBucketNameOutput",
            value=self.storage_stack.data_bucket.bucket_name,
            description="Name of the S3 data lake bucket",
            export_name="mps-data-bucket-name"
        )

        CfnOutput(
            self, "DataBucketArnOutput",
            value=self.storage_stack.data_bucket.bucket_arn,
            description="ARN of the S3 data lake bucket",
            export_name="mps-data-bucket-arn"
        )

        CfnOutput(
            self, "DataFetcherLambdaNameOutput",
            value=self.ingestion_stack.data_fetcher_lambda.function_name,
            description="Name of the data fetcher Lambda function",
            export_name="mps-data-fetcher-lambda-name"
        )

        CfnOutput(
            self, "DataFetcherLambdaArnOutput",
            value=self.ingestion_stack.data_fetcher_lambda.function_arn,
            description="ARN of the data fetcher Lambda function",
            export_name="mps-data-fetcher-lambda-arn"
        )