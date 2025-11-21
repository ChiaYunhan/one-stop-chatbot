#!/usr/bin/env python3
import aws_cdk as cdk
from stacks.s3_stack import S3Stack
from stacks.bedrock_stack import BedrockStack
from stacks.iam_roles_stack import RolesStack
from stacks.api_gateway_stack import ApiGatewayStack
from stacks.lambda_layer_stack import LambdaLayerStack
from stacks import environment as env
import os


app = cdk.App()
cdk_env = cdk.Environment(region=os.environ.get("CDK_DEFAULT_REGION", "us-east-1"))

s3_stack = S3Stack(app, f"{env.PROJECT_NAME}-S3Stack", env=cdk_env)

role_stack = RolesStack(
    app,
    f"{env.PROJECT_NAME}-RoleStack",
    env=cdk_env,
    storage=s3_stack,
)

layer_stack = LambdaLayerStack(app, f"{env.PROJECT_NAME}-LayerStack", env=cdk_env)

bedrock_stack = BedrockStack(
    app,
    f"{env.PROJECT_NAME}-BedrockStack",
    storage=s3_stack,
    roles=role_stack,
    env=cdk_env,
)

api_gateway_stack = ApiGatewayStack(
    app,
    f"{env.PROJECT_NAME}-ApiGatewayStack",
    storage=s3_stack,
    roles=role_stack,
    bedrock=bedrock_stack,
    env=cdk_env,
)

# Dependencies
role_stack.add_dependency(s3_stack)

bedrock_stack.add_dependency(s3_stack)
bedrock_stack.add_dependency(role_stack)

api_gateway_stack.add_dependency(layer_stack)
api_gateway_stack.add_dependency(bedrock_stack)

# Frontend is handled by frontend_app.py

app.synth()
