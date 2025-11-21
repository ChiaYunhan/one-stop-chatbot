import boto3
import os
import json
from datetime import datetime
from botocore.client import ClientError
from aws_lambda_powertools import Logger

logger = Logger()

KNOWLEDGE_BASE_ID = os.environ.get("KNOWLEDGE_BASE_ID")
DATA_SOURCE_ID = os.environ.get("DATA_SOURCE_ID")
KNOWLEDGE_BASE_BUCKET = os.environ.get("KNOWLEDGE_BASE_BUCKET")

S3_CLIENT = boto3.client("s3")
BEDROCK_AGENT_CLIENT = boto3.client("bedrock-agent")


def lambda_handler(event, context):
    try:
        request_body = json.loads(event.get("body"))
        if not request_body:
            raise Exception("body invalid")

        docs_to_be_deleted = request_body.get("documents")
        response = delete_s3_files(docs_to_be_deleted)
        formatted_response = format_response(response)

        return create_response(200, "Success", formatted_response)

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


def delete_s3_files(docs):
    sync_required = False
    delete_objects = []

    for doc in docs:
        if doc["status"] in ["INDEXED", "PARTIALLY_INDEXED"]:
            sync_required = True

        s3_key = doc["s3Key"].rsplit("/", 3)[-1]
        delete_object = {"Key": s3_key}
        delete_objects.append(delete_object)

    response = S3_CLIENT.delete_objects(
        Bucket=KNOWLEDGE_BASE_BUCKET, Delete={"Objects": delete_objects}
    )

    if sync_required:
        sync_knowledge_base()

    return response


def sync_knowledge_base():
    response = BEDROCK_AGENT_CLIENT.start_ingestion_job(
        knowledgeBaseId=KNOWLEDGE_BASE_ID,
        dataSourceId=DATA_SOURCE_ID,
        description=f"Sync triggered at {datetime.now().isoformat()}",
    )


def format_response(resp):
    deleted = [item["Key"] for item in resp.get("Deleted", [])]

    failed = [err["Key"] for err in resp.get("Errors", [])]

    return {
        "success": len(failed) == 0,
        "deletedCount": len(deleted),
        "failedIds": failed,
    }


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
