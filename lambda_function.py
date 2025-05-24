import json
from datetime import datetime
from typing import List, Optional, Set
import boto3
from aws_lambda_powertools import Logger
from aws_lambda_powertools.event_handler import LambdaFunctionUrlResolver
from aws_lambda_powertools.utilities.typing import LambdaContext
from pydantic import BaseModel, Field

# Initialize logger and clients
logger = Logger()
s3 = boto3.client("s3")

# Configuration
ARTICLES_FILE = "articles.json"

# Initialize Function URL resolver
app = LambdaFunctionUrlResolver()


class Article(BaseModel):
    url: str
    title: str
    source: str
    excerpt: str
    tags: List[str]
    photo_url: Optional[str]
    timestamp: datetime = Field(default_factory=datetime.now)

    model_config = {"frozen": True, "arbitrary_types_allowed": True}

    def __eq__(self, other):
        if not isinstance(other, Article):
            return False
        return (
            self.url == other.url
            and self.title == other.title
            and self.source == other.source
            and self.excerpt == other.excerpt
            and self.tags == other.tags
            and self.photo_url == other.photo_url
        )

    def __hash__(self):
        # Use a tuple of immutable values for hashing
        # Sort tags to ensure consistent hashing regardless of tag order
        return hash(
            (
                self.url,
                self.title,
                self.source,
                self.excerpt,
                tuple(sorted(self.tags)),
                self.photo_url,
            )
        )

    def model_dump(self):
        return {
            **super().model_dump(),
            "timestamp": self.timestamp.isoformat(),
        }


def get_bucket_name():
    ssm = boto3.client("ssm")
    resp = ssm.get_parameter(Name="/diy-pocket/bucket", WithDecryption=True)
    return resp["Parameter"]["Value"]


def load_articles() -> Set[Article]:
    """Load articles from S3 and convert to Article objects."""
    try:
        response = s3.get_object(Bucket=get_bucket_name(), Key=ARTICLES_FILE)
        articles_data = json.loads(response["Body"].read().decode("utf-8"))
        return {Article(**article) for article in articles_data}
    except s3.exceptions.NoSuchKey:
        return set()
    except Exception as e:
        logger.error(f"Error loading articles: {str(e)}")
        raise


def save_articles(articles: Set[Article]) -> None:
    """Save Article objects to S3 as JSON"""
    try:
        articles_data = [article.model_dump() for article in articles]
        content = json.dumps(articles_data).encode("utf-8")
        logger.info(
            s3.put_object(
                Bucket=get_bucket_name(),
                Key=ARTICLES_FILE,
                Body=content,
                ContentType="application/json",
                ContentEncoding="gzip",
            )
        )
    except Exception as e:
        logger.error(f"Error saving articles: {str(e)}")
        raise


@app.post("/save")
def save_article():
    try:
        body = app.current_event.json_body
        articles = load_articles()
        logger.info(f"Loaded {len(articles)} articles")

        new_article = Article(**body)
        logger.info(f"Parsed article: {new_article}")
        articles.add(new_article)

        save_articles(articles)

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
