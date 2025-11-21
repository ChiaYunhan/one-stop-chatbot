import os
import boto3
import json
import uuid
from botocore.exceptions import ClientError
from aws_lambda_powertools import Logger
from datetime import datetime
from urllib.parse import unquote


KNOWLEDGE_BASE_ID = os.environ.get("KNOWLEDGE_BASE_ID")
DATA_SOURCE_ID = os.environ.get("DATA_SOURCE_ID")
KNOWLEDGE_BASE_BUCKET = os.environ.get("KNOWLEDGE_BASE_BUCKET")

BEDROCK_AGENT_CLIENT = boto3.client("bedrock-agent")
S3_CLIENT = boto3.client("s3")

logger = Logger()


class DateTimeEncoder(json.JSONEncoder):
    """Custom JSON encoder that handles datetime objects"""

    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)


def lambda_handler(event, context):

    try:

        s3_documents = list_s3_documents()
        knowledge_base_documents = list_knowledge_base_documents(100)
        merged_documents = merge_documents(s3_documents, knowledge_base_documents)

        formatted_response = format_response(merged_documents)

        return create_response(
            200, "Successfully retrieved documents", formatted_response
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


def list_s3_documents():
    documents = []
    paginator = S3_CLIENT.get_paginator("list_objects_v2")

    pages = paginator.paginate(Bucket=KNOWLEDGE_BASE_BUCKET)

    for page in pages:
        for obj in page.get("Contents", []):
            if obj["Key"].endswith("/"):
                continue

            display_name = obj["Key"].split("/")[-1]
            documents.append(
                {
                    "id": str(uuid.uuid4()),
                    "knowledgeBaseId": None,
                    "dataSourceId": None,
                    "status": "NOT_INDEXED",
                    "s3Key": f's3://{KNOWLEDGE_BASE_BUCKET}/{obj["Key"]}',
                    "statusReason": "Knowledge base sync has not been triggered || Issue with knowledge base syncing check knowledge base on management console",
                    "updatedAt": obj["LastModified"].isoformat(),
                    "displayName": display_name,
                }
            )

    logger.info(documents)

    return documents


def list_knowledge_base_documents(max_results):
    documents = []
    next_token = None

    while True:
        params = {
            "knowledgeBaseId": KNOWLEDGE_BASE_ID,
            "dataSourceId": DATA_SOURCE_ID,
            "maxResults": min(max_results - len(documents), 100),
        }

        if next_token:
            params["nextToken"] = next_token

        response = BEDROCK_AGENT_CLIENT.list_knowledge_base_documents(**params)

        for document in response.get("documentDetails"):
            s3_uri = document.get("identifier", {}).get("s3", {}).get("uri", "")
            display_name = s3_uri.split("/")[-1]

            formatted_doc = {
                "id": str(uuid.uuid4()),
                "knowledgeBaseId": document.get("knowledgeBaseId"),
                "dataSourceId": document.get("dataSourceId"),
                "status": document.get("status"),
                "s3Key": document.get("identifier", {}).get("s3", {}).get("uri"),
                "statusReason": document.get("statusReason", ""),
                "updatedAt": document.get("updatedAt").isoformat(),
                "displayName": display_name,
            }
            documents.append(formatted_doc)

        next_token = response.get("nextToken")
        if not next_token or len(documents) >= max_results:
            break

    return documents


def merge_documents(s3_documents, knowledge_base_documents):
    kb_docs_map = {doc["s3Key"]: doc for doc in knowledge_base_documents}
    logger.info(kb_docs_map)

    merged = []

    for s3_doc in s3_documents:
        logger.info(s3_doc["s3Key"])
        if s3_doc["s3Key"] in kb_docs_map:
            merged.append(kb_docs_map[s3_doc["s3Key"]])
            del kb_docs_map[s3_doc["s3Key"]]

        else:
            merged.append(s3_doc)

    for kb_doc in kb_docs_map.values():
        kb_doc["statusReason"] = "File not found in S3"
        merged.append(kb_doc)

    return sorted(merged, key=lambda doc: doc["updatedAt"] or "", reverse=True)


def format_response(merged_documents):

    for doc in merged_documents:
        doc["s3Key"] = unquote(doc["s3Key"])

    return {
        "documentDetails": merged_documents,
    }


def create_response(status_code, message, payload=None):
    if not payload:
        payload = {}

    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Content-Security-Policy": "default-src 'self'; script-src 'self'",
            "X-Content-Type-Options": "nosniff",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains; preload",
            "Cache-control": "no-store",
            "Pragma": "no-cache",
            "X-Frame-Options": "SAMEORIGIN",
        },
        "body": json.dumps(
            {"statusCode": status_code, "message": message, **payload},
            cls=DateTimeEncoder,
        ),
    }
