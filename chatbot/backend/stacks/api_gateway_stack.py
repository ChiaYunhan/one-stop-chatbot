# api_gateway_stack.py

from asyncio import timeout_at
from aws_cdk import (
    Stack,
    aws_lambda as lambda_,
    aws_apigateway as apigateway,
    aws_ssm as ssm,
    aws_logs as logs,
    Duration,
    Tags,
)
from datetime import datetime
from .environment import *
from constructs import Construct

THROTTLE_RATE_LIMIT = 10
THROTTLE_BURST_LIMIT = 20
MONTHLY_QUOTA = 900_000  # Stay under 1M API Gateway requests
LOG_RETENTION_DAYS = "ONE_WEEK"


class ApiGatewayStack(Stack):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        storage: Stack,
        roles: Stack,
        bedrock: Stack,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)
        Tags.of(self).add(key="PROJECT", value=PROJECT_NAME)

        lambda_dir = "./lambda/functions/"

        ############################################

        #                  LAYERS                  #

        ############################################

        LambdaCoreLayer = lambda_.LayerVersion.from_layer_version_arn(
            self,
            "LambdaCoreLayer",
            ssm.StringParameter.from_string_parameter_name(
                self, "LambdaCoreLayerArn", f"{PROJECT_NAME}-LambdaCoreLayerArn"
            ).string_value,
        )

        ############################################

        #                 LAMBDAS                  #

        ############################################

        ListDocument = lambda_.Function(
            self,
            id=f"{PROJECT_NAME}-ListDocument",
            function_name=f"{PROJECT_NAME}-ListDocument",
            runtime=lambda_.Runtime.PYTHON_3_12,
            handler="lambda_function.lambda_handler",
            code=lambda_.Code.from_asset(lambda_dir + "ListDocuments"),
            layers=[LambdaCoreLayer],
            description="Function to fetch list of documents in knowledge base",
            role=roles.api_lambda_role,
            environment={
                "KNOWLEDGE_BASE_ID": bedrock.knowledge_base.get_response_field(
                    "knowledgeBase.knowledgeBaseId"
                ),
                "DATA_SOURCE_ID": bedrock.data_source.get_response_field(
                    "dataSource.dataSourceId"
                ),
                "KNOWLEDGE_BASE_BUCKET": storage.knowledge_base_bucket.bucket_name,
            },
            timeout=Duration.seconds(30),
            tracing=lambda_.Tracing.ACTIVE,
            memory_size=128,
            log_retention=logs.RetentionDays(LOG_RETENTION_DAYS),
        )

        GenerateDownloadDocumentLink = lambda_.Function(
            self,
            id=f"{PROJECT_NAME}-GenerateDownloadDocumentLink",
            function_name=f"{PROJECT_NAME}-GenerateDownloadDocumentLink",
            runtime=lambda_.Runtime.PYTHON_3_12,
            handler="lambda_function.lambda_handler",
            code=lambda_.Code.from_asset(lambda_dir + "GenerateDownloadDocumentLink"),
            layers=[LambdaCoreLayer],
            description="Function to generate s3 download presigned url",
            role=roles.api_lambda_role,
            environment={},
            timeout=Duration.seconds(30),
            tracing=lambda_.Tracing.ACTIVE,
            memory_size=128,
            log_retention=logs.RetentionDays(LOG_RETENTION_DAYS),
        )

        GenerateUploadDocumentLink = lambda_.Function(
            self,
            id=f"{PROJECT_NAME}-GenerateUploadDocumentLink",
            function_name=f"{PROJECT_NAME}-GenerateUploadDocumentLink",
            runtime=lambda_.Runtime.PYTHON_3_12,
            handler="lambda_function.lambda_handler",
            code=lambda_.Code.from_asset(lambda_dir + "GenerateUploadDocumentLink"),
            layers=[LambdaCoreLayer],
            description="Function to generate s3 upload presigned url",
            role=roles.api_lambda_role,
            environment={
                "KNOWLEDGE_BASE_BUCKET": storage.knowledge_base_bucket.bucket_name
            },
            timeout=Duration.seconds(30),
            tracing=lambda_.Tracing.ACTIVE,
            memory_size=128,
            log_retention=logs.RetentionDays(LOG_RETENTION_DAYS),
        )

        TriggerIngestDocumentsKnowledgeBase = lambda_.Function(
            self,
            id=f"{PROJECT_NAME}-TriggerIngestDocumentsKnowledgeBase",
            function_name=f"{PROJECT_NAME}-TriggerIngestDocumentsKnowledgeBase",
            runtime=lambda_.Runtime.PYTHON_3_12,
            handler="lambda_function.lambda_handler",
            code=lambda_.Code.from_asset(
                lambda_dir + "TriggerIngestDocumentsKnowledgeBase"
            ),
            layers=[LambdaCoreLayer],
            description="Function to trigger knowledge base sync after updating documents in s3 bucket",
            role=roles.api_lambda_role,
            environment={
                "KNOWLEDGE_BASE_ID": bedrock.knowledge_base.get_response_field(
                    "knowledgeBase.knowledgeBaseId"
                ),
                "DATA_SOURCE_ID": bedrock.data_source.get_response_field(
                    "dataSource.dataSourceId"
                ),
            },
            timeout=Duration.seconds(30),
            tracing=lambda_.Tracing.ACTIVE,
            memory_size=128,
            log_retention=logs.RetentionDays(LOG_RETENTION_DAYS),
        )

        DeleteDocuments = lambda_.Function(
            self,
            id=f"{PROJECT_NAME}-DeleteDocuments",
            function_name=f"{PROJECT_NAME}-DeleteDocuments",
            runtime=lambda_.Runtime.PYTHON_3_12,
            handler="lambda_function.lambda_handler",
            code=lambda_.Code.from_asset(lambda_dir + "DeleteDocuments"),
            layers=[LambdaCoreLayer],
            description="Function to documents in s3 bucket",
            role=roles.api_lambda_role,
            environment={
                "KNOWLEDGE_BASE_ID": bedrock.knowledge_base.get_response_field(
                    "knowledgeBase.knowledgeBaseId"
                ),
                "DATA_SOURCE_ID": bedrock.data_source.get_response_field(
                    "dataSource.dataSourceId"
                ),
                "KNOWLEDGE_BASE_BUCKET": storage.knowledge_base_bucket.bucket_name,
            },
            timeout=Duration.seconds(30),
            tracing=lambda_.Tracing.ACTIVE,
            memory_size=128,
            log_retention=logs.RetentionDays(LOG_RETENTION_DAYS),
        )

        ############################################

        #                API GATEWAY               #

        ############################################

        ApiGateWay = apigateway.RestApi(
            self,
            id=f"{PROJECT_NAME}-RestApi",
            description=f"{PROJECT_NAME} REST API",
            deploy=False,
            endpoint_configuration={"types": [apigateway.EndpointType.REGIONAL]},
            cloud_watch_role=True,
            default_cors_preflight_options=apigateway.CorsOptions(
                allow_origins=apigateway.Cors.ALL_ORIGINS,  # Equivalent to ["*"]
                allow_methods=["POST", "OPTIONS"],
                allow_headers=[
                    "Content-Type",
                    "X-Amz-Date",
                    "Authorization",
                    "X-Api-Key",
                    "X-Amz-Security-Token",
                ],
                # allow_credentials=False is the default
            ),
        )

        # POST /documents
        DocumentApiResource = ApiGateWay.root.add_resource("documents")

        # POST /documents/list
        DocumentListApiResource = DocumentApiResource.add_resource("list")
        ListDocumentFunctionIntegration = apigateway.LambdaIntegration(ListDocument)
        ListDocumentPostApiMethod = DocumentListApiResource.add_method(
            "POST", ListDocumentFunctionIntegration
        )

        # POST /documents/downloadpresignedurl
        DocumentDownloadPresignedUrlResource = DocumentApiResource.add_resource(
            "downloadpresignedurl"
        )
        GenerateDownloadDocumentLinkFunctionIntegration = apigateway.LambdaIntegration(
            GenerateDownloadDocumentLink
        )
        GenerateDownloadDocumentLinkPostApiMethod = (
            DocumentDownloadPresignedUrlResource.add_method(
                "POST", GenerateDownloadDocumentLinkFunctionIntegration
            )
        )

        # POST /documents/downloadpresignedurl
        DocumentUploadPresignedUrlResource = DocumentApiResource.add_resource(
            "uploadpresignedurl"
        )
        GenerateUploadDocumentLinkFunctionIntegration = apigateway.LambdaIntegration(
            GenerateUploadDocumentLink
        )
        GenerateUploadDocumentLinkPostApiMethod = (
            DocumentUploadPresignedUrlResource.add_method(
                "POST", GenerateUploadDocumentLinkFunctionIntegration
            )
        )

        # POST /documents/sync
        DocumentListApiResource = DocumentApiResource.add_resource("sync")
        TriggerIngestDocumentsKnowledgeBaseFunctionIntegration = (
            apigateway.LambdaIntegration(TriggerIngestDocumentsKnowledgeBase)
        )
        TriggerIngestDocumentsKnowledgeBasePostApiMethod = (
            DocumentListApiResource.add_method(
                "POST", TriggerIngestDocumentsKnowledgeBaseFunctionIntegration
            )
        )

        # POST /documents/delete
        DeleteDocumentApiResource = DocumentApiResource.add_resource("delete")
        DeleteDocumentFunctionIntegration = apigateway.LambdaIntegration(
            DeleteDocuments
        )
        DeleteDocumentPostApiMethod = DeleteDocumentApiResource.add_method(
            "POST", DeleteDocumentFunctionIntegration
        )

        ############################################

        #             API GATEWAY CONFIG           #

        ############################################

        ApiGateWayDeployment = apigateway.Deployment(
            self,
            id=f"{PROJECT_NAME}-ApiDeployment={datetime.now().isoformat()}",
            api=ApiGateWay,
            retain_deployments=False,
        )

        ApiGateWayStage = apigateway.Stage(
            self,
            id=f"{PROJECT_NAME}-ApiStage",
            stage_name="chatbot",
            deployment=ApiGateWayDeployment,
            throttling_rate_limit=THROTTLE_RATE_LIMIT,
            throttling_burst_limit=THROTTLE_BURST_LIMIT,
            tracing_enabled=True,
            logging_level=apigateway.MethodLoggingLevel.OFF,
            data_trace_enabled=False,
            metrics_enabled=True,
        )

        usage_plan = ApiGateWay.add_usage_plan(
            f"{PROJECT_NAME}-UsagePlan",
            name=f"{PROJECT_NAME}-UsagePlan",
            description="Free tier optimized usage plan",
            quota=(
                apigateway.QuotaSettings(
                    limit=MONTHLY_QUOTA,
                    period=apigateway.Period.MONTH,
                )
                if MONTHLY_QUOTA
                else None
            ),
            throttle=apigateway.ThrottleSettings(
                rate_limit=THROTTLE_RATE_LIMIT,
                burst_limit=THROTTLE_BURST_LIMIT,
            ),
        )
