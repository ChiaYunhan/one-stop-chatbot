import uuid
import boto3
import json
import os
import re
from aws_lambda_powertools import Logger
from botocore.client import ClientError
from datetime import datetime, timezone


logger = Logger()

KNOWLEDGE_BASE_ID = os.environ.get("KNOWLEDGE_BASE_ID")
MODEL_ARN = os.environ.get("MODEL_ARN")

BEDROCK_AGENT_RUNTIME_CLIENT = boto3.client("bedrock-agent-runtime")


class DateTimeEncoder(json.JSONEncoder):
    """Custom JSON encoder that handles datetime objects"""

    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)


def clean_citation_markers(text):
    """Remove citation markers like %[1]%, %[2]%, etc. from the text"""
    cleaned_text = re.sub(r"%\[(\d+)\]%", r"[\1]", text)

    cleaned_text = re.sub(r"\s*,\s*,", ",", cleaned_text)
    cleaned_text = re.sub(r",\s*:", ":", cleaned_text)
    cleaned_text = re.sub(r"\s+", " ", cleaned_text)
    cleaned_text = cleaned_text.strip()

    return cleaned_text


def lambda_handler(event, context):

    try:

        request_body = json.loads(event["body"])
        user_query, session_id = extract_details(request_body)

        bedrock_response = query_knowledge_base(user_query, session_id)
        formatted_response = format_response(bedrock_response)

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


def extract_details(request_body):
    user_query = request_body["messages"][-1]["content"]
    session_id = request_body.get("sessionId", None)

    return user_query, session_id


def query_knowledge_base(user_query, session_id=None):
    retrieve_request = {
        "input": {"text": user_query},
        "retrieveAndGenerateConfiguration": {
            "type": "KNOWLEDGE_BASE",
            "knowledgeBaseConfiguration": {
                "knowledgeBaseId": KNOWLEDGE_BASE_ID,
                "modelArn": MODEL_ARN,
                "retrievalConfiguration": {
                    "vectorSearchConfiguration": {
                        "numberOfResults": 10,  # Increased for better citations
                        "overrideSearchType": "SEMANTIC",
                    }
                },
                "generationConfiguration": {
                    "promptTemplate": {
                        "textPromptTemplate": """You are a helpful AI assistant. Use ONLY the following context to answer the user's question accurately and helpfully.

Retrieved context: $search_results$

User question: $query$

IMPORTANT INSTRUCTIONS:
- Base your answer ONLY on the provided context
- For every fact or piece of information you mention, reference the specific source document
- If you cannot find the answer in the provided context, clearly state that the information is not available in the retrieved documents
- Structure your response clearly with proper citations
- Use markdown formatting for better readability

Please provide a helpful and accurate response based on the retrieved context."""
                    }
                },
            },
        },
    }

    if session_id:
        retrieve_request["sessionId"] = session_id

    bedrock_response = BEDROCK_AGENT_RUNTIME_CLIENT.retrieve_and_generate(
        **retrieve_request
    )

    logger.info(bedrock_response)

    return bedrock_response


def format_response(bedrock_response):
    session_id = bedrock_response["sessionId"]
    response_text = bedrock_response["output"]["text"]
    citations = bedrock_response["citations"]

    cleaned_response_text = clean_citation_markers(response_text)

    citation_references = []

    for citation in citations:
        for reference in citation["retrievedReferences"]:
            page_number = "Unknown"
            if (
                "metadata" in reference
                and "x-amz-bedrock-kb-document-page-number" in reference["metadata"]
            ):
                page_number = reference["metadata"][
                    "x-amz-bedrock-kb-document-page-number"
                ]

            reference_obj = {
                "page": page_number,
                "file": reference["location"]["s3Location"]["uri"].split("/")[-1],
            }

            citation_references.append(reference_obj)

    message_obj = {
        "assistantMessage": {
            "id": str(uuid.uuid4()),
            "role": "ASSISTANT",
            "content": cleaned_response_text,
            "citation": citation_references,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
        "sessionId": session_id,
    }

    return message_obj


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
            {
                "statusCode": status_code,
                "message": message,
                **payload,
            },
            cls=DateTimeEncoder,
        ),
    }
