import argparse
from datetime import datetime
import time
import requests
import json
import os
from dotenv import load_dotenv


def main(commit: bool = False) -> bool:
    load_dotenv("local.env")
    endpoint = os.getenv("API_ENDPOINT") or "http://localhost:8000"
    payload = {
        "url": "https://example.com/test-article",
        "title": "Test Article Title",
        "source": "Test Source",
        "excerpt": "This is a test article excerpt for testing the API endpoint.",
        "tags": ["test", "api", "development"],
        "photo_url": "https://example.com/test-photo.jpg",
    }
    headers = {
        "Content-Type": "application/json",
        "x-auth-token": os.getenv("AUTH_TOKEN"),
    }

    try:
        print(f"POST {endpoint}")
        ts = datetime.now()
        response = requests.post(
            endpoint,
            json=payload,
            headers=headers,
        )

        print(f"{response.status_code} {(datetime.now() - ts).total_seconds()}s")
        print(json.dumps(response.json(), indent=2))
        for key, value in response.headers.items():
            print(f"{key}: {value}")

        status = response.status_code == 200
        print(f"status: {status}")
        print(f"wrote to s3://{os.getenv('BUCKET_NAME')}/articles.json")
        if commit:
            time.sleep(2)
            ts = datetime.now()
            print(f"PATCH {endpoint}")
            response = requests.patch(
                endpoint,
                headers=headers,
            )
            print(f"{response.status_code} {(datetime.now() - ts).total_seconds()}s")
            print(json.dumps(response.json(), indent=2))
            status = status and response.status_code == 200
        return status

    except requests.exceptions.RequestException as e:
        print(f"\nError making request: {e}")
        return False


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Test the save API endpoint by posting an article."
    )
    parser.add_argument(
        "--commit",
        action="store_true",
    )
    args = parser.parse_args()
    main(args.commit)
