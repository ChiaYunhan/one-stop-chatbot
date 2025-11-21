# bedrock_stack.py

from aws_cdk import Stack, aws_iam as iam, custom_resources as cr, Tags
from constructs import Construct
from .environment import *


class BedrockStack(Stack):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        storage: Stack,
        roles: Stack,
        **kwargs,
    ):
        super().__init__(scope, construct_id, **kwargs)

        Tags.of(self).add(key="PROJECT", value=PROJECT_NAME)

        self.storage = storage
        self.roles = roles

        self.vector_bucket = self._create_vector_bucket()
        self.vector_index = self._create_vector_index()
        self.knowledge_base = self._create_knowledge_base()
        self.data_source = self._create_data_source()

    def _create_vector_bucket(self) -> cr.AwsCustomResource:
        self.vector_bucket_name = f"{PROJECT_NAME}-vector-bucket"

        create_vector_bucket = cr.AwsCustomResource(
            self,
            "CreateVectorBucket",
            on_create=cr.AwsSdkCall(
                service="s3vectors",
                action="createVectorBucket",
                parameters={"vectorBucketName": self.vector_bucket_name},
                output_paths=["vectorBucketArn"],
                physical_resource_id=cr.PhysicalResourceId.of(self.vector_bucket_name),
            ),
            on_delete=cr.AwsSdkCall(
                service="s3vectors",
                action="deleteVectorBucket",
                parameters={"vectorBucketName": self.vector_bucket_name},
            ),
            policy=cr.AwsCustomResourcePolicy.from_statements(
                [
                    iam.PolicyStatement(
                        actions=[
                            "s3vectors:CreateVectorBucket",
                            "s3vectors:DeleteVectorBucket",
                        ],
                        resources=["*"],
                    )
                ]
            ),
            install_latest_aws_sdk=True,
        )

        return create_vector_bucket

    def _create_vector_index(self) -> cr.AwsCustomResource:
        self.vector_index_name = "bedrock-kb-index"

        create_vector_index = cr.AwsCustomResource(
            self,
            "CreateVectorIndex",
            on_create=cr.AwsSdkCall(
                service="s3vectors",
                action="createIndex",
                parameters={
                    "vectorBucketName": self.vector_bucket_name,
                    "indexName": self.vector_index_name,
                    "dimension": 1024,
                    "distanceMetric": "cosine",
                    "dataType": "float32",
                    "metadataConfiguration": {
                        "nonFilterableMetadataKeys": [
                            "AMAZON_BEDROCK_TEXT",  # for s3 vectors this is effectively required, read further: https://docs.aws.amazon.com/bedrock/latest/userguide/knowledge-base-setup.html
                        ],
                    },
                },
                physical_resource_id=cr.PhysicalResourceId.of(
                    f"{self.vector_bucket_name}/{self.vector_index_name}"
                ),
                output_paths=["indexArn"],
            ),
            on_delete=cr.AwsSdkCall(
                service="s3vectors",
                action="deleteIndex",
                parameters={
                    "vectorBucketName": self.vector_bucket_name,
                    "indexName": self.vector_index_name,
                },
            ),
            policy=cr.AwsCustomResourcePolicy.from_statements(
                [
                    iam.PolicyStatement(
                        actions=[
                            "s3vectors:CreateIndex",
                            "s3vectors:DeleteIndex",
                        ],
                        resources=["*"],
                    )
                ]
            ),
            install_latest_aws_sdk=True,
        )

        create_vector_index.node.add_dependency(self.vector_bucket)

        return create_vector_index

    def _create_knowledge_base(self) -> cr.AwsCustomResource:
        knowledge_base_name = f"{PROJECT_NAME}-knowledge-base-{self.account}"

        create_kb = cr.AwsCustomResource(
            self,
            "CreateKnowledgeBase",
            on_create=cr.AwsSdkCall(
                service="bedrock-agent",
                action="createKnowledgeBase",
                parameters={
                    "name": knowledge_base_name,
                    "roleArn": self.roles.knowledge_base_role.role_arn,
                    "knowledgeBaseConfiguration": {
                        "type": "VECTOR",
                        "vectorKnowledgeBaseConfiguration": {
                            "embeddingModelArn": f"arn:aws:bedrock:{self.region}::foundation-model/amazon.titan-embed-text-v2:0",
                            "embeddingDataType": "FLOAT32",
                        },
                    },
                    "storageConfiguration": {
                        "type": "S3_VECTORS",
                        "s3VectorsConfiguration": {
                            "vectorBucketArn": self.vector_bucket.get_response_field(
                                "vectorBucketArn"
                            ),
                            "indexArn": self.vector_index.get_response_field(
                                "indexArn"
                            ),
                        },
                    },
                },
                physical_resource_id=cr.PhysicalResourceId.from_response(
                    "knowledgeBase.knowledgeBaseId"
                ),
            ),
            on_delete=cr.AwsSdkCall(
                service="bedrock-agent",
                action="deleteKnowledgeBase",
                parameters={"knowledgeBaseId": cr.PhysicalResourceIdReference()},
            ),
            on_update=cr.AwsSdkCall(
                service="bedrock-agent",
                action="getKnowledgeBase",
                parameters={"knowledgeBaseId": cr.PhysicalResourceIdReference()},
            ),
            policy=cr.AwsCustomResourcePolicy.from_statements(
                [
                    iam.PolicyStatement(
                        actions=[
                            "bedrock:*",
                            "bedrock-agent:*",
                        ],
                        resources=["*"],
                    ),
                    iam.PolicyStatement(
                        actions=["iam:PassRole"],
                        resources=[self.roles.knowledge_base_role.role_arn],
                    ),
                ]
            ),
            install_latest_aws_sdk=True,
        )

        create_kb.node.add_dependency(self.vector_bucket)
        create_kb.node.add_dependency(self.vector_index)

        return create_kb

    def _create_data_source(self):
        create_data_source = cr.AwsCustomResource(
            self,
            "CreateDataSource",
            on_create=cr.AwsSdkCall(
                service="bedrock-agent",
                action="createDataSource",
                parameters={
                    "knowledgeBaseId": self.knowledge_base.get_response_field(
                        "knowledgeBase.knowledgeBaseId"
                    ),
                    "name": "data-source",
                    "dataSourceConfiguration": {
                        "type": "S3",
                        "s3Configuration": {
                            "bucketArn": self.storage.knowledge_base_bucket.bucket_arn,
                        },
                    },
                },
                physical_resource_id=cr.PhysicalResourceId.from_response(
                    "dataSource.dataSourceId"
                ),
            ),
            on_delete=cr.AwsSdkCall(
                service="bedrock-agent",
                action="deleteDataSource",
                parameters={
                    "knowledgeBaseId": self.knowledge_base.get_response_field(
                        "knowledgeBase.knowledgeBaseId"
                    ),
                    "dataSourceId": cr.PhysicalResourceIdReference(),
                },
            ),
            policy=cr.AwsCustomResourcePolicy.from_statements(
                [
                    iam.PolicyStatement(
                        actions=[
                            "bedrock:CreateDataSource",
                            "bedrock:DeleteDataSource",
                        ],
                        resources=["*"],
                    ),
                ],
            ),
            install_latest_aws_sdk=True,
        )

        create_data_source.node.add_dependency(self.knowledge_base)

        return create_data_source
