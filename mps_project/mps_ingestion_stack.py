from constructs import Construct
from aws_cdk import (
    Duration,
    Stack,
    CfnOutput,
    RemovalPolicy,
    aws_iam as iam,
    aws_lambda as _lambda,
    aws_logs as logs,
    aws_s3 as s3,
)

class MpsIngestionStack(Stack):
    """
    Ingestion Stack for MPS Project.
    
    Creates a Lambda function that fetches data and writes to S3 bucket.
    
    Args:
        data_bucket: S3 Bucket instance where Lambda will write data
    """

    def __init__(self, scope: Construct, construct_id: str, data_bucket: s3.Bucket, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Validate input
        if not isinstance(data_bucket, s3.Bucket):
            raise TypeError("data_bucket must be an s3.Bucket instance")

        self.data_bucket = data_bucket
        
        # Create IAM Role for Lambda execution
        lambda_role = iam.Role(
            self,
            id="MPS-LambdaRole",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            description="IAM Role for MPS Lambda Function",
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "service-role/AWSLambdaBasicExecutionRole"
                ),
            ],
        )

        # Create Lambda function for data fetching
        self.data_fetcher_lambda = _lambda.Function(
            self,
            id="MPS-DataFetcher",
            function_name="mps-data-fetcher",
            runtime=_lambda.Runtime.PYTHON_3_10,
            code=_lambda.Code.from_asset(
                path="lambda",
                bundling={
                    "image": _lambda.Runtime.PYTHON_3_10.bundling_image,
                    "command": [
                        "bash",
                        "-c",
                        "pip install -r requirements.txt -t /asset-output && cp -r . /asset-output",
                    ],
                },
            ),
            handler="data_fetcher.handler",
            role=lambda_role,
            timeout=Duration.seconds(30),
            memory_size=256,
            environment={
                "LOG_LEVEL": "INFO",
                "BUCKET_NAME": self.data_bucket.bucket_name,
                "BUCKET_ARN": self.data_bucket.bucket_arn,
            },
            log_retention=logs.RetentionDays.ONE_WEEK,
        )

        # Grant Lambda write permissions to the bucket
        self.data_bucket.grant_write(self.data_fetcher_lambda.role)

        # Export outputs
        CfnOutput(
            self, "DataFetcherLambdaNameOutput",
            value=self.data_fetcher_lambda.function_name,
            description="Name of the data fetcher Lambda function"
        )

        CfnOutput(
            self, "DataFetcherLambdaArnOutput",
            value=self.data_fetcher_lambda.function_arn,
            description="ARN of the data fetcher Lambda function"
        )
