from constructs import Construct
from aws_cdk import (
    Stack,
    CfnOutput,
)
from .mps_ingestion_stack import MpsIngestionStack
from .mps_storage_stack import StorageStack
from .mps_catalog_stack import CatalogStack

class MpsProjectStack(Stack):
    """
    Main stack that orchestrates the MPS Project infrastructure.
    
    Components:
    - Storage Stack: S3 bucket for data lake
    - Ingestion Stack: Lambda function for data fetching
    """

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        name_stacks = {
            "storage":"MPS-StorageStack",
            "ingestion":"MPS-IngestionStack",
            "catalog":"MPS-CatalogStack",
        }
        
        # Create data storage stack
        self.storage_stack = StorageStack(
            self, 
            construct_id=name_stacks["storage"],
            stack_name=name_stacks["storage"]
        )

        # Create data ingestion stack
        self.ingestion_stack = MpsIngestionStack(
            self, 
            construct_id=name_stacks["ingestion"],
            stack_name=name_stacks["ingestion"],
            data_bucket=self.storage_stack.data_bucket,
        )

        # Define explicit dependency
        self.ingestion_stack.add_dependency(self.storage_stack)

        # Grant Lambda write permissions to S3 bucket
        self.storage_stack.data_bucket.grant_write(
            self.ingestion_stack.data_fetcher_lambda.role
        )

        # 3. Create catalog stack
        self.catalog_stack = CatalogStack(
            self, 
            construct_id=name_stacks["catalog"],
            stack_name=name_stacks["catalog"],
            data_bucket=self.storage_stack.data_bucket
        )

        # El Crawler debe esperar a que el Bucket exista
        self.catalog_stack.add_dependency(self.storage_stack)

        # Export key outputs for external access
        CfnOutput(
            self, 
            id="DataBucketNameOutput",
            description="Name of the S3 data lake bucket",
            export_name="mps-data-bucket-name", 
            value=self.storage_stack.data_bucket.bucket_name
        )

        CfnOutput(
            self, 
            id="DataBucketArnOutput",
            description="ARN of the S3 data lake bucket",
            export_name="mps-data-bucket-arn",
            value=self.storage_stack.data_bucket.bucket_arn
        )

        CfnOutput(
            self, 
            id="DataFetcherLambdaNameOutput",
            description="Name of the data fetcher Lambda function",
            export_name="mps-data-fetcher-lambda-name", 
            value=self.ingestion_stack.data_fetcher_lambda.function_name
        )

        CfnOutput(
            self, 
            id="DataFetcherLambdaArnOutput",
            description="ARN of the data fetcher Lambda function",
            export_name="mps-data-fetcher-lambda-arn", 
            value=self.ingestion_stack.data_fetcher_lambda.function_arn
        )