import boto3
import os
import json
from botocore.client import Config
from aws_lambda_powertools import Logger
from botocore.client import ClientError
from datetime import datetime
import uuid

KNOWLEDGE_BASE_BUCKET = os.environ.get("KNOWLEDGE_BASE_BUCKET")
S3_CLIENT = boto3.client("s3", config=Config(signature_version="s3v4"))

UPLOAD_CONFIGS = {
    "document": {
        "bucket": KNOWLEDGE_BASE_BUCKET,
        "path_prefix": "",
        "allowed_extensions": ["pdf", "png", "jpg", "jpeg"],
        "max_file_size": 15728640,  # 15MB
        "expiration": 3600,  # 1 hour
    },
}

logger = Logger()


def lambda_handler(event, context):
    try:
        request_body = json.loads(event["body"])
        files = request_body["files"]

        results = []

        for file_info in files:
            try:
                upload_type = file_info.get("uploadType", "document")
                file_name = file_info["fileName"]
                file_type = file_info.get("fileType", "")

                configs = UPLOAD_CONFIGS[upload_type]

                # Verify file extension
                file_ext = verify_file_extension(
                    file_name, configs["allowed_extensions"]
                )

                # Generate unique key
                base_name = os.path.splitext(file_name)[0]
                key = (
                    f"{configs['path_prefix']}/{base_name}.{file_ext}"
                    if configs["path_prefix"]
                    else f"{base_name}.{file_ext}"
                )

                # Generate presigned POST
                presigned_post = generate_presigned_post(
                    configs["bucket"],
                    key,
                    configs["max_file_size"],
                    configs["expiration"],
                    file_type,
                )

                results.append(
                    {"fileName": file_name, "success": True, **presigned_post}
                )

            except Exception as e:
                results.append(
                    {"fileName": file_name, "success": False, "error": str(e)}
                )

        return create_response(200, "Success", {"results": results})

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


def verify_file_extension(file_name, allowed_extensions):
    if "." not in file_name:
        raise Exception("Invalid file name")

    file_ext = file_name.rsplit(".", 1)[-1].lower()
    if file_ext not in allowed_extensions:
        raise Exception(f"File extension '{file_ext}' not allowed")
    return file_ext


def generate_presigned_post(
    bucket_name, object_name, max_file_size, expiration, content_type: None
):
    conditions = [["content-length-range", 0, max_file_size]]
    fields = {}

    if content_type:
        conditions.append({"Content-Type": content_type})
        fields["Content-Type"] = content_type

    response = S3_CLIENT.generate_presigned_post(
        Bucket=bucket_name,
        Key=object_name,
        Fields=fields,
        Conditions=conditions,
        ExpiresIn=expiration,
    )

    return {"url": response["url"], "fields": response["fields"], "key": object_name}


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
