#!/usr/bin/env python3
import requests
import json
import argparse
from datetime import datetime

def test_article_submission(api_url):
    """
    Test the article submission endpoint with a sample payload
    """
    # Sample article payload
    payload = {
        "url": "https://example.com/test-article",
        "title": "Test Article Title",
        "source": "Test Source",
        "excerpt": "This is a test article excerpt for testing the API endpoint.",
        "tags": ["test", "api", "development"],
        "photo_url": "https://example.com/test-photo.jpg"
    }

    try:
        # Send POST request
        response = requests.post(
            api_url,
            json=payload,
            headers={'Content-Type': 'application/json'}
        )

        # Print response details
        print(f"\nRequest sent at: {datetime.now()}")
        print(f"Status Code: {response.status_code}")
        print("\nResponse Headers:")
        for key, value in response.headers.items():
            print(f"{key}: {value}")
        
        print("\nResponse Body:")
        try:
            print(json.dumps(response.json(), indent=2))
        except json.JSONDecodeError:
            print(response.text)

        return response.status_code == 200

    except requests.exceptions.RequestException as e:
        print(f"\nError making request: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Test API Gateway endpoint for article submission')
    parser.add_argument('api_url', help='The API Gateway endpoint URL')
    args = parser.parse_args()

    print(f"Testing API endpoint: {args.api_url}")
    print("Sending test article payload...")
    
    success = test_article_submission(args.api_url)
    
    if success:
        print("\nTest completed successfully!")
    else:
        print("\nTest failed!")
        exit(1)

if __name__ == "__main__":
    main() 