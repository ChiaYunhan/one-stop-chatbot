#!/usr/bin/env python3
import aws_cdk as cdk
from stacks.frontend_stack import FrontendStack
from stacks import environment as env
import os


app = cdk.App()
cdk_env = cdk.Environment(region=os.environ.get("CDK_DEFAULT_REGION", "us-east-1"))

# Frontend-only app - requires api_url context
frontend_stack = FrontendStack(
    app,
    f"{env.PROJECT_NAME}-FrontendStack",
    env=cdk_env,
)

app.synth()
