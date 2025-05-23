# DIY Pocket Lambda Function

AWS Lambda function that receives a POST with url, title, source, excerpt, list of tags, and photo url.

## API Endpoint

The Lambda function exposes a POST endpoint at `/article` that accepts the following JSON payload:

```json
{
    "url": "https://example.com/article",
    "title": "Article Title",
    "source": "Source Name",
    "excerpt": "Article excerpt or summary",
    "tags": ["tag1", "tag2", "tag3"],
    "photo_url": "https://example.com/photo.jpg" // Optional
}
```

## Response

Successful response (200):
```json
{
    "message": "Article saved successfully",
}
```

Error response (400):
```json
{
    "error": "Error message details"
}
```

## Development and Deployment

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. First time deployment

Create diy-pocket-save Lambda in AWS console.

```bash
make setup-api
```

3. Save ROLE_ARN

Add Lambda details to `local.env`


4. Deploy to AWS Lambda:
```bash
# Update existing function
make build update-lambda
```

Required environment variables:
- `ROLE_ARN` - AWS IAM Role ARN for Lambda execution
- `FUNCTION_NAME` - Lambda function name (defaults to diy-pocket-save)

Lambda Function Configuration:
- Runtime: Python 3.9
- Handler: main.lambda_handler
- Memory: 128 MB
- Timeout: 30 seconds

# Save a story

AWS Lambda function receives a POST with url, title, source, excerpt, list of tags, and photo url.
Validate requester is authorized: comes from specific url.
Append datetime, url, title, source, tags, and excerpt to compressed JSON file in S3 bucket.

# Review stories
Create index.html that
  - Load stories JSON from S3 bucket.
  - Sort stories by datetime descending.
  - Display stories using bootstrap cards.

Add dropdowns on the top of the page for source and tags.
On select a dropdown, filter results to match the source or tags.