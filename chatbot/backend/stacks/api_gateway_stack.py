# api_gateway_stack.py

from aws_cdk import (
    Stack,
    aws_lambda as lambda_,
    aws_iam as iam,
    aws_apigateway as aws_apigateway,
    aws_ssm as ssm,
)
import os
from constructs import Construct


class ApiGatewayStack(Stack):
    def __init__(
        self, scope: Construct, construct_id: str, project_name: str, **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

    lambda_dir = "./lambda/functions/"
