from constructs import Construct
from aws_cdk import Stack
from .mps_ingestion_stack import MpsIngestionStack

class MpsProjectStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Queue data ingestion stack
        self.ingestion_stack = MpsIngestionStack(
            self, "IngestionStack",
            stack_name="mps-ingestion-stack"
        )