import json
import os
from aws_lambda_powertools import Logger
from save import save_article

logger = Logger()

CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type,x-auth-token",
    "Access-Control-Allow-Methods": "OPTIONS,POST"
}

def handle_options():
    logger.info(f"CORS preflight request: {CORS_HEADERS}")
    return {
        "statusCode": 200,
        "headers": CORS_HEADERS,
        "body": ""
    }

def handle_post(event):
    headers = event.get("headers", {})
    auth_token = headers.get("x-auth-token")
    if not auth_token or auth_token != os.getenv("AUTH_TOKEN"):
        return {
            "statusCode": 403,
            "headers": CORS_HEADERS,
            "body": json.dumps({"error": "Forbidden: Invalid or missing x-auth-token header"})
        }
    try:
        body = event.get("body")
        if event.get("isBase64Encoded"):
            import base64
            body = base64.b64decode(body).decode()
        data = json.loads(body)
        logger.info(f"POST article data: {data}")
        save_article(data)
        return {
            "statusCode": 200,
            "headers": CORS_HEADERS,
            "body": json.dumps({"status": "ok"})
        }
    except Exception as e:
        logger.error(f"Error processing article: {str(e)}")
        return {
            "statusCode": 400,
            "headers": CORS_HEADERS,
            "body": json.dumps({"error": str(e)})
        }

def lambda_handler(event, context):
    method = event.get("requestContext", {}).get("http", {}).get("method", "")
    if method == "OPTIONS":
        return handle_options()
    if method == "POST":
        return handle_post(event)
    return {
        "statusCode": 405,
        "headers": CORS_HEADERS,
        "body": json.dumps({"error": "Method not allowed"})
    }
