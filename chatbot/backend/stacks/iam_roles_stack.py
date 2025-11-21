# iam_roles_stack.py

from aws_cdk import Stack, aws_iam as iam, Tags
from constructs import Construct
from .environment import *


class RolesStack(Stack):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        storage: Stack,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        Tags.of(self).add(key="PROJECT", value=PROJECT_NAME)

        self.knowledge_base_bucket = storage.knowledge_base_bucket

        self.api_lambda_role = self._create_api_lambda_role()
        self.knowledge_base_role = self._create_knowledge_base_role()
        self.processing_lambda_role = self._create_processing_lambda_role()

    def _create_api_lambda_role(self) -> iam.Role:
        """Role for lambda to access dynamodb and s3"""
        role = iam.Role(
            self,
            f"{PROJECT_NAME}-ApiLambdaRole",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            description="Role for API Gateway Lambda functions",
        )

        role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name("AdministratorAccess")
        )

        return role

    def _create_knowledge_base_role(self) -> iam.Role:
        """
        SERVICE ROLE for Bedrock Knowledge Base
        This role is ASSUMED BY Bedrock service (not by you)
        Bedrock uses this role to access S3, embeddings, and vector store
        """
        role = iam.Role(
            self,
            f"{PROJECT_NAME}-KnowledgeBaseServiceRole",
            assumed_by=iam.ServicePrincipal("bedrock.amazonaws.com"),
            description="Service role for Bedrock Knowledge Base to access resources",
        )

        role.add_to_policy(
            iam.PolicyStatement(
                sid="BedrockModelAccess",
                effect=iam.Effect.ALLOW,
                actions=["bedrock:InvokeModel"],
                resources=[
                    f"arn:aws:bedrock:{self.region}::foundation-model/amazon.titan-embed-text-v2:0"
                ],
            )
        )

        # S3 Vectors Data-Plane Operations
        role.add_to_policy(
            iam.PolicyStatement(
                sid="S3VectorsDataPlane",
                effect=iam.Effect.ALLOW,
                actions=[
                    "s3vectors:PutVectors",
                    "s3vectors:GetVectors",
                    "s3vectors:ListVectors",
                    "s3vectors:QueryVectors",
                    "s3vectors:DeleteVectors",
                ],
                resources=[
                    "*"
                ],  # S3 Vectors doesn't support resource-level permissions yet
            )
        )

        # S3 Vectors Control-Plane Operations (for validation during KB creation)
        role.add_to_policy(
            iam.PolicyStatement(
                sid="S3VectorsControlPlane",
                effect=iam.Effect.ALLOW,
                actions=[
                    "s3vectors:CreateVectorBucket",
                    "s3vectors:GetVectorBucket",
                    "s3vectors:DeleteVectorBucket",
                    "s3vectors:CreateIndex",
                    "s3vectors:GetIndex",
                    "s3vectors:DeleteIndex",
                    "s3vectors:ListIndexes",
                ],
                resources=["*"],
            )
        )

        role.add_to_policy(
            iam.PolicyStatement(
                sid="CloudWatchLogs",
                effect=iam.Effect.ALLOW,
                actions=[
                    "logs:CreateLogGroup",
                    "logs:CreateLogStream",
                    "logs:PutLogEvents",
                    "logs:DescribeLogGroups",
                    "logs:DescribeLogStreams",
                ],
                resources=[
                    f"arn:aws:logs:{self.region}:{self.account}:log-group:/aws/bedrock/*",
                    f"arn:aws:logs:{self.region}:{self.account}:log-group:/aws/bedrock/*:*",
                ],
            )
        )

        self.knowledge_base_bucket.grant_read(role)

        return role

    def _create_processing_lambda_role(self) -> iam.Role:
        role = iam.Role(
            self,
            f"{PROJECT_NAME}-ProcessingLambdaRole",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            description="Role for processing lambdas that interact with bedrock, s3 and dynamodb",
        )

        role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "bedrock:InvokeModel",
                    "bedrock:InvokeModelWithResponseStream",
                ],
                resources=[f"arn:aws:bedrock:{self.region}::foundation-model/*"],
            )
        )

        role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=["bedrock:Retrieve", "bedrock:RetrieveAndGenerate"],
                resources=[
                    f"arn:aws:bedrock:{self.region}:{self.account}:knowledge-base/*"
                ],
            )
        )

        return role
