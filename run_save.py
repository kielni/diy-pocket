#!/usr/bin/env python3
import requests
import json
import os


def main():
    """
    Test the article submission endpoint with a sample payload
    """
    endpoint = os.getenv("API_ENDPOINT") or "http://localhost:8000"
    # Sample article payload
    payload = {
        "url": "https://example.com/test-article",
        "title": "Test Article Title",
        "source": "Test Source",
        "excerpt": "This is a test article excerpt for testing the API endpoint.",
        "tags": ["test", "api", "development"],
        "photo_url": "https://example.com/test-photo.jpg",
    }

    try:
        # Send POST request
        print(f"POST {endpoint}")
        response = requests.post(
            endpoint,
            json=payload,
            headers={"Content-Type": "application/json"},
        )

        # Print response details
        print(f"{response.status_code}")
        print(json.dumps(response.json(), indent=2))
        for key, value in response.headers.items():
            print(f"{key}: {value}")

        return response.status_code == 200

    except requests.exceptions.RequestException as e:
        print(f"\nError making request: {e}")
        return False


if __name__ == "__main__":
    main()
