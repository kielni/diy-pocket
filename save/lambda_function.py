import json
import os
import traceback
from aws_lambda_powertools import Logger
from save import save_pending_article, write_pending

logger = Logger()

CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type,x-auth-token",
    "Access-Control-Allow-Methods": "OPTIONS,POST",
}


def handle_options():
    logger.info(f"CORS preflight request: {CORS_HEADERS}")
    return {"statusCode": 200, "headers": CORS_HEADERS, "body": ""}


def check_auth_token(event):
    headers = event.get("headers", {})
    auth_token = headers.get("x-auth-token")
    if not auth_token or auth_token != os.getenv("AUTH_TOKEN"):
        return {
            "statusCode": 403,
            "headers": CORS_HEADERS,
            "body": json.dumps(
                {"error": "Forbidden: Invalid or missing x-auth-token header"}
            ),
        }
    return None


def handle_post(event):
    resp = check_auth_token(event)
    if resp:
        return resp
    try:
        body = event.get("body")
        data = json.loads(body)
        logger.info(f"POST article data: {data}")
        key = save_pending_article(data)
        return {
            "statusCode": 200,
            "headers": CORS_HEADERS,
            "body": json.dumps({"key": key}),
        }
    except Exception as e:
        logger.error(f"Error processing article: {str(e)}")
        traceback.print_exc()
        return {
            "statusCode": 400,
            "headers": CORS_HEADERS,
            "body": json.dumps({"error": str(e)}),
        }


def handle_patch(event):
    resp = check_auth_token(event)
    if resp:
        return resp
    pending, total = write_pending()
    return {
        "statusCode": 200,
        "body": json.dumps({"status": "ok", "pending": pending, "total": total}),
    }


def lambda_handler(event, context):
    if event.get("source") and event.get("detail-type"):
        logger.info(f"Received EventBridge event: {event}")
        pending, total = write_pending()
        logger.info(
            f"EventBridge: processed {pending} pending, total {total} articles."
        )
        return {
            "statusCode": 200,
            "body": json.dumps({"status": "ok", "pending": pending, "total": total}),
        }
    method = event.get("requestContext", {}).get("http", {}).get("method", "")
    if method == "OPTIONS":
        return handle_options()
    if method == "POST":
        return handle_post(event)
    if method == "PATCH":
        return handle_patch(event)
    return {
        "statusCode": 405,
        "headers": CORS_HEADERS,
        "body": json.dumps({"error": "Method not allowed"}),
    }
