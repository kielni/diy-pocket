import argparse
import gzip
import json
import logging
from datetime import datetime
from io import BytesIO
from typing import List, Optional, Set
import boto3
from pydantic import BaseModel, Field

log = logging.getLogger("save")
s3 = boto3.client("s3")

ARTICLES_FILE = "articles.json"


class Article(BaseModel):
    url: str
    title: str
    source: Optional[str] = None
    excerpt: str
    tags: List[str]
    photo_url: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)

    model_config = {"frozen": True, "arbitrary_types_allowed": True}

    def __eq__(self, other):
        if not isinstance(other, Article):
            return False
        return (
            self.url == other.url
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
        log.info(f"load s3://{get_bucket_name()}/{ARTICLES_FILE}")
        body = response["Body"].read()
        with open("temp.json.gz", "wb") as f:
            f.write(body)
        with gzip.GzipFile(fileobj=BytesIO(body)) as gz:
            data = gz.read().decode("utf-8")
        return {Article(**article) for article in json.loads(data)}
    except s3.exceptions.NoSuchKey:
        return set()
    except Exception as e:
        log.error(f"Error loading articles: {str(e)}")
        raise


def save_articles(articles: Set[Article]) -> None:
    """Save Article objects to S3 as JSON"""
    try:
        articles_data = [article.model_dump() for article in articles]
        content = json.dumps(articles_data).encode("utf-8")
        content = gzip.compress(content)
        log.info(
            s3.put_object(
                Bucket=get_bucket_name(),
                Key=ARTICLES_FILE,
                Body=content,
                ContentType="application/json",
                ContentEncoding="gzip",
            )
        )
    except Exception as e:
        log.error(f"Error saving articles: {str(e)}")
        raise


def save_article(body: dict):
    articles = load_articles()
    log.info(f"Loaded {len(articles)} articles")
    new_article = Article(**body)
    log.info(f"Parsed article: {new_article}")
    articles.add(new_article)
    save_articles(articles)


def to_articles(docs: List[dict]) -> Set[Article]:
    """Convert a list of dictionaries to a set of Article objects."""
    articles = set()
    for doc in docs:
        try:
            article = Article(**doc)
            articles.add(article)
        except Exception as e:
            log.error(f"Error parsing article: {str(e)}")
    return articles


def parse_file(filename: str):
    with open(args.filename, "r") as f:
        body = json.load(f)
    new_articles = to_articles(body)
    log.info(f"Parsed {len(new_articles)} articles")
    articles = new_articles | load_articles()
    log.info(f"total {len(new_articles)} articles")
    save_articles(articles)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser()
    parser.add_argument("filename", type=str)
    args = parser.parse_args()
    parse_file(args.filename)
