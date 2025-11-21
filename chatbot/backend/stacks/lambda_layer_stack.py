import os
import subprocess
from aws_cdk import Stack, RemovalPolicy, aws_lambda as lambda_, Tags, aws_ssm as ssm
from constructs import Construct
from .environment import *


class LambdaLayerStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        Tags.of(self).add(key="PROJECT", value=PROJECT_NAME)

        LambdaCoreLayer = lambda_.LayerVersion(
            self,
            "LambdaCoreLayer",
            layer_version_name=f"{PROJECT_NAME}-LambdaCoreLayer",
            code=self.create_dependencies_layer("./lambda/layers/LambdaCore"),
            description="Lambda Layer with AwsLambdaPowertTools and boto3",
            removal_policy=RemovalPolicy.DESTROY,
        )

        ssm.StringParameter(
            self,
            "LambdaCoreLayerArn",
            string_value=LambdaCoreLayer.layer_version_arn,
            type=ssm.ParameterType.STRING,
            description="ARN for LambdaCoreLayer",
            parameter_name=f"{PROJECT_NAME}-LambdaCoreLayerArn",
        )

    def create_dependencies_layer(self, localPath):
        main_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        while localPath[0] == "." or localPath[0] == "/":
            localPath = localPath[1:]

        layerPath = f"{main_dir}/{localPath}"

        if not os.path.exists(f"{layerPath}/python"):
            subprocess.check_call(
                f"pip install -r {layerPath}/requirements.txt -t {layerPath}/python",
                shell=True,
            )
        return lambda_.Code.from_asset(layerPath)
