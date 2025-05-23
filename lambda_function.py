import json
from typing import List, Optional
from aws_lambda_powertools import Logger
from aws_lambda_powertools.event_handler import APIGatewayRestResolver
from aws_lambda_powertools.utilities.typing import LambdaContext
from pydantic import BaseModel, HttpUrl

# Initialize logger
logger = Logger()

# Initialize API Gateway resolver
app = APIGatewayRestResolver()


class ArticleInput(BaseModel):
    url: HttpUrl
    title: str
    source: str
    excerpt: str
    tags: List[str]
    photo_url: Optional[HttpUrl]


@app.post("/save")
def save_article():
    try:
        # Parse request body
        body = app.current_event.json_body
        article = ArticleInput(**body)

        # Log the received article
        logger.info(
            "Received article",
            extra={
                "title": article.title,
                "source": article.source,
                "tags": article.tags,
            },
        )

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
