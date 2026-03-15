import boto3
import json
import os
from datetime import datetime

def get_s3_client():
    """
    Creates an S3 client.
    We use boto3.client() (low-level) instead of boto3.resource() (high-level)
    because for S3 file uploads, the client API is simpler.
    """
    return boto3.client(
        "s3",
        region_name=os.getenv("AWS_REGION", "us-east-1")
    )

def save_raw_to_s3(raw_data: list, source: str, search_term: str) -> str:
    """
    Saves the raw API response to S3 as a JSON file.

    The file path is organized by:
      raw/{source}/{year}/{month}/{day}/{timestamp}_{search_term}.json

    Example:
      raw/adzuna/2024/01/15/143022_python_developer.json

    This is called "partitioning by date" — makes it easy to:
    - Find data from a specific day
    - Query with Athena later (Step 7)
    - Apply lifecycle rules (archive old data)
    """
    s3 = get_s3_client()
    bucket_name = os.getenv("S3_BUCKET_NAME", "job-analyzer-data-lake-dev-ingr")

    # Create the file path using current date/time.
    now = datetime.utcnow()

    # Clean the search term for use in filename (replace spaces with underscores).
    clean_search = search_term.replace(" ", "_")

    # Build the S3 key (path).
    # This is NOT a folder structure — S3 is flat — but the "/" makes it LOOK
    # like folders in the AWS Console.
    key = f"raw/{source}/{now:%Y}/{now:%m}/{now:%d}/{now:%H%M%S}_{clean_search}.json"

    # Upload the data to S3.
    # json.dumps() converts the Python list/dict to a JSON string.
    s3.put_object(
        Bucket=bucket_name,
        Key=key,
        Body=json.dumps(raw_data, indent=2),
        ContentType="application/json"
    )

    # Return the full S3 path for logging.
    return f"s3://{bucket_name}/{key}"