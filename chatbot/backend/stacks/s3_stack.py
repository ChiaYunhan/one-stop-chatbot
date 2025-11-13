# s3_stack.py

from aws_cdk import Stack, aws_s3 as s3, RemovalPolicy, Tags
from constructs import Construct


class S3Stack(Stack):
    def __init__(
        self, scope: Construct, construct_id: str, project_name: str, **kwargs
    ):
        super().__init__(scope, construct_id, **kwargs)

        Tags.of(self).add(key="PROJECT", value="CHATBOT")

        self.project_name = project_name
        self.knowledge_base_bucket = self._create_knowledge_base_bucket()

    def _create_knowledge_base_bucket(self) -> s3.Bucket:
        bucket = s3.Bucket(
            self,
            "KnowledgeBaseDocumentBucket",
            bucket_name=f"{self.project_name}-document-bucket-{self.account}",
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True,
            enforce_ssl=True,
            cors=[
                s3.CorsRule(
                    allowed_methods=[
                        s3.HttpMethods.GET,
                        s3.HttpMethods.POST,
                        s3.HttpMethods.PUT,
                    ],
                    allowed_origins=["*"],
                    allowed_headers=["*"],
                )
            ],
        )

        return bucket
