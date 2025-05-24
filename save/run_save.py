import requests
import json
import os
from dotenv import load_dotenv

def main():
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

    try:
        print(f"POST {endpoint}")
        response = requests.post(
            endpoint,
            json=payload,
            headers={"Content-Type": "application/json", "x-auth-token": os.getenv("AUTH_TOKEN")},
        )

        print(f"{response.status_code}")
        print(json.dumps(response.json(), indent=2))
        for key, value in response.headers.items():
            print(f"{key}: {value}")

        print(f"wrote to s3://{os.getenv('BUCKET')}/articles.json")
        return response.status_code == 200

    except requests.exceptions.RequestException as e:
        print(f"\nError making request: {e}")
        return False


if __name__ == "__main__":
    main()
