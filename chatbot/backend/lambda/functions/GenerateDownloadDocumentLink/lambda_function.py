import json
import boto3
from aws_lambda_powertools import Logger
from botocore.client import Config, ClientError

S3_CLIENT = boto3.client("s3", config=Config(signature_version="s3v4"))
logger = Logger()


def lambda_handler(event, context):
    try:
        request_body = json.loads(event["body"])
        s3_key = request_body["s3Key"]
        action = request_body.get("action", "download")  # "download" or "view"

        s3_key = s3_key.replace("%2F", "/")
        presigned_url = generate_presigned_url(s3_key, action)

        formatted_response = format_response(presigned_url)
        logger.info(formatted_response)
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


def generate_presigned_url(s3_key, action="download", expiration=3600):
    bucket = s3_key.split("/")[2]
    s3_file_path = s3_key.rsplit("/", 3)[-1]
    file_name = s3_file_path.split("/")[-1]

    params = {
        "Bucket": bucket,
        "Key": s3_file_path,
    }

    if action == "download":
        params["ResponseContentDisposition"] = "attachment"
    elif action == "view":
        params["ResponseContentDisposition"] = f"inline ; filename={file_name}"
        params["ResponseContentType"] = "application/pdf"

    response = S3_CLIENT.generate_presigned_url(
        "get_object",
        Params=params,
        ExpiresIn=expiration,
    )

    return response


def format_response(presigned_url):
    return {"url": presigned_url}


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
        ),
    }
