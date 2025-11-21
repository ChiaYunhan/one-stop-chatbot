import boto3
import os
import json
from aws_lambda_powertools import Logger
from datetime import datetime
from botocore.client import ClientError

logger = Logger()

KNOWLEDGE_BASE_ID = os.environ.get("KNOWLEDGE_BASE_ID")
DATA_SOURCE_ID = os.environ.get("DATA_SOURCE_ID")

BEDROCK_AGENT_CLIENT = boto3.client("bedrock-agent")


def lambda_handler(event, context):
    """Trigger Knowledge Base sync after file uploads"""
    try:
        response = BEDROCK_AGENT_CLIENT.start_ingestion_job(
            knowledgeBaseId=KNOWLEDGE_BASE_ID,
            dataSourceId=DATA_SOURCE_ID,
            description=f"Sync triggered at {datetime.now().isoformat()}",
        )

        ingestion_job = response["ingestionJob"]

        return create_response(
            200,
            "Success",
            {
                "ingestionJobId": ingestion_job["ingestionJobId"],
                "status": ingestion_job["status"],
                "startedAt": (
                    ingestion_job["startedAt"].isoformat()
                    if "startedAt" in ingestion_job
                    else None
                ),
            },
        )

    except ClientError as e:
        http_status = e.response["ResponseMetadata"]["HTTPStatusCode"]
        error_code = e.response["Error"]["Code"]
        error_message = e.response["Error"]["Message"]

        logger.exception(f"AWS Error: {error_code} - {error_message}")

        return create_response(
            http_status,
            f"The server encountered an issue with AWS.",
            {"error": error_message, "code": error_code},
        )

    except Exception as e:
        logger.exception(str(e))
        return create_response(
            500,
            f"The server encountered an unexpected condition that prevented it from fulfilling your request.",
            {"error": str(e)},
        )


def create_response(status_code, message, payload=None):
    if not payload:
        payload = {}

    response_body = {"statusCode": status_code, "message": message, **payload}

    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Content-Type",
            "Access-Control-Allow-Methods": "POST, OPTIONS",
        },
        "body": json.dumps(response_body),
    }
