import json
from aws_lambda_powertools import Logger
from aws_lambda_powertools.event_handler import LambdaFunctionUrlResolver
from aws_lambda_powertools.utilities.typing import LambdaContext
from save import save_article

logger = Logger()
app = LambdaFunctionUrlResolver()


@app.post("/save")
def save_article_request():
    try:
        save_article(app.current_event.json_body)

        return {"statusCode": 200, "body": json.dumps({"status": "ok"})}

    except Exception as e:
        logger.error(f"Error processing article: {str(e)}")
        return {"statusCode": 400, "body": json.dumps({"error": str(e)})}


@logger.inject_lambda_context
def lambda_handler(event: dict, context: LambdaContext) -> dict:
    """
    Main Lambda handler function
    """
    return app.resolve(event, context)
