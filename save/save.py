import argparse
import gzip
import json
import logging
import os
import re
from datetime import datetime
from io import BytesIO
from typing import List, Optional, Set
import boto3
from pydantic import BaseModel, Field

log = logging.getLogger("save")
s3 = boto3.client("s3")

ARTICLES_FILE = "articles.json"
PENDING_PATH = "pending-articles"


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
        return self.url == other.url

    def __hash__(self):
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
    return os.getenv("BUCKET_NAME", None)


def load_articles() -> Set[Article]:
    """Load articles from S3 and convert to Article objects."""
    try:
        response = s3.get_object(Bucket=get_bucket_name(), Key=ARTICLES_FILE)
        log.info(f"load s3://{get_bucket_name()}/{ARTICLES_FILE}")
        body = response["Body"].read()
        with gzip.GzipFile(fileobj=BytesIO(body)) as gz:
            data = gz.read().decode("utf-8")
        log.info(f"Loaded {len(data)} bytes from S3")
        return {Article(**article) for article in json.loads(data)}
    except s3.exceptions.NoSuchKey:
        return set()
    except Exception as e:
        log.error(f"Error loading articles: {str(e)}")
        raise


def save_articles(articles: Set[Article]) -> None:
    """Save Article objects to S3 as JSON"""
    try:
        bucket_name = get_bucket_name()
        articles_data = [article.model_dump() for article in articles]
        content = json.dumps(articles_data, indent=2).encode("utf-8")
        content = gzip.compress(content)
        log.info(
            s3.put_object(
                Bucket=bucket_name,
                Key=ARTICLES_FILE,
                Body=content,
                ContentType="application/json",
                ContentEncoding="gzip",
            )
        )
        log.info(
            f"Saved {len(articles)} articles to s3://{bucket_name}/{ARTICLES_FILE}"
        )
    except Exception as e:
        log.error(f"Error saving articles: {str(e)}")
        raise


def write_pending() -> tuple[int, int]:
    """Load all articles, process all pending articles, and save the combined set."""
    bucket_name = get_bucket_name()
    response = s3.list_objects_v2(Bucket=bucket_name, Prefix=PENDING_PATH)
    pending_files = [
        item["Key"]
        for item in response.get("Contents", [])
        if item["Key"].endswith(".json.gz")
    ]
    log.info(f"Found {len(pending_files)} pending files in {PENDING_PATH}")
    if not pending_files:
        log.info("No pending files to process.")
        return 0, 0
    articles = load_articles()
    for key in pending_files:
        try:
            obj = s3.get_object(Bucket=bucket_name, Key=key)
            article_data = json.loads(obj["Body"].read())
            article = Article(**article_data)
            articles.add(article)
            log.info(f"Processed pending article from {key}")
        except Exception as e:
            log.error(f"Error processing pending file {key}: {str(e)}")
    save_articles(articles)
    for key in pending_files:
        try:
            s3.delete_object(Bucket=bucket_name, Key=key)
        except Exception as e:
            log.error(f"Error deleting pending file {key}: {str(e)}")
    return len(pending_files), len(articles)


def save_pending_article(body: dict) -> str:
    """Save a pending article to S3."""
    try:
        bucket_name = get_bucket_name()
        content = json.dumps(body, indent=2).encode("utf-8")
        url = re.sub(r"\W", "_", body.get("url"))
        key = f"{PENDING_PATH}/{url}.json.gz"
        s3.put_object(
            Bucket=bucket_name,
            Key=key,
            Body=content,
            ContentType="application/json",
            ContentEncoding="gzip",
        )
        log.info(f"Saved pending article to s3://{bucket_name}/{key}")
        return key
    except Exception as e:
        log.error(f"Error saving pending article: {str(e)}")
        raise


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
