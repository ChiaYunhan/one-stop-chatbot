from datetime import datetime
import uuid
import boto3
import json
import os
from aws_lambda_powertools import Logger
from botocore.client import ClientError

KNOWLEDGE_BASE_ID = os.environ.get("KNOWLEDGE_BASE_ID")
MODEL_ARN = os.environ.get("MODEL_ARN")

BEDROCK_AGENT_RUNTIME_CLIENT = boto3.client("bedrock-agent-runtime")


class DateTimeEncoder(json.JSONEncoder):
    """Custom JSON encoder that handles datetime objects"""

    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)


def lambda_handler(event, context):

    request_body = json.loads(event["body"])
    user_query, session_id = extract_details(request_body)

    bedrock_response = query_knowledge_base(user_query, session_id)
    formatted_response = format_response(bedrock_response)

    return create_response(200, "Success", formatted_response)


def extract_details(request_body):
    user_query = request_body["messages"][-1]
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
                        "numberOfResults": 5,
                        "overrideSearchType": "SEMANTIC",
                    }
                },
                "generationConfiguration": {
                    "promptTemplate": {
                        "textPromptTemplate": """You are a helpful AI assistant. Use the following context to answer the user's question accurately and helpfully. If the context doesn't contain enough information to answer the question, say so clearly.

Retrieved context: $search_results$

User question: $query$

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

    return bedrock_response


def format_response(bedrock_response):
    session_id = bedrock_response["sessionId"]
    response_text = bedrock_response["output"]["text"]
    citations = bedrock_response["citations"]

    citation_references = []

    for citation in citations:
        for reference in citation["retrievedReferences"]:
            reference_obj = {
                "text": reference["content"]["text"],
                "file": reference["location"]["s3Location"]["uri"].split("/")[-1],
            }

            citation_references.append(reference_obj)

    message_obj = {
        "assistantMessage": {
            "id": str(uuid.uuid4()),
            "role": "ASSISTANT",
            "content": response_text,
            "citation": citation_references,
            "timestamp": datetime.now().isoformat(),
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
