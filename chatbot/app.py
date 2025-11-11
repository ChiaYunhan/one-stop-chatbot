#!/usr/bin/env python3
import aws_cdk as cdk
from stacks.s3_stack import S3Stack
from stacks.bedrock_stack import BedrockStack
from stacks.iam_roles_stack import RolesStack
from stacks.api_gateway_stack import ApiGatewayStack
from stacks import environment as env
import os


app = cdk.App()
cdk_env = cdk.Environment(region=os.environ.get("CDK_DEFAULT_REGION", "us-east-1"))

role_stack = RolesStack(
    app, f"{env.PROJECT_NAME}-RoleStack", project_name=env.PROJECT_NAME, env=cdk_env
)
s3_stack = S3Stack(
    app, f"{env.PROJECT_NAME}-S3Stack", project_name=env.PROJECT_NAME, env=cdk_env
)
bedrock_stack = BedrockStack(
    app,
    f"{env.PROJECT_NAME}-BedrockStack",
    storage=s3_stack,
    roles=role_stack,
    project_name=env.PROJECT_NAME,
    env=cdk_env,
)
api_gateway_stack = ApiGatewayStack(
    app,
    f"{env.PROJECT_NAME}-ApiGatewayStack",
    project_name=env.PROJECT_NAME,
    env=cdk_env,
)


bedrock_stack.add_dependency(s3_stack)
bedrock_stack.add_dependency(role_stack)
app.synth()
