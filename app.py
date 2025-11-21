#!/usr/bin/env python3

import aws_cdk as cdk

from mps_project.mps_project_stack import MpsProjectStack

app = cdk.App()
MpsProjectStack(
    app, 
    construct_id="MPS-ProjectStack", 
    stack_name="MPS-ProjectStack",
    description="MPS Project Stack - Data Ingestion, Storage and Data catalog Infrastructure"
    )

app.synth()
