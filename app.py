#!/usr/bin/env python3

import aws_cdk as cdk

from mps_project.mps_project_stack import MpsProjectStack


app = cdk.App()
MpsProjectStack(app, "MpsProjectStack", stack_name="mps-project-stack")

app.synth()
