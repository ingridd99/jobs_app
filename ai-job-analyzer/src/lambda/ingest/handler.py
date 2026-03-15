import json
import boto3
import os
import requests
from datetime import datetime


def get_adzuna_jobs(what, country):
    """
    Fetches jobs from Adzuna API.
    Same logic as src/clients/adzuna_client.py but self-contained
    because Lambda needs all code in one place.
    """
    app_id = os.getenv("ADZUNA_APP_ID")
    app_key = os.getenv("ADZUNA_APP_KEY")

    url = f"https://api.adzuna.com/v1/api/jobs/{country}/search/1"
    params = {
        "app_id": app_id,
        "app_key": app_key,
        "what": what,
        "results_per_page": 50,
        "content-type": "application/json",
    }

    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()

    return data.get("results", [])


def save_raw_to_s3(s3_client, raw_data, source, search_term):
    """
    Saves raw API response to S3.
    Same logic as src/clients/s3_client.py.
    """
    bucket_name = os.getenv("S3_BUCKET_NAME")
    now = datetime.utcnow()
    clean_search = search_term.replace(" ", "_")

    key = f"raw/{source}/{now:%Y}/{now:%m}/{now:%d}/{now:%H%M%S}_{clean_search}.json"

    s3_client.put_object(
        Bucket=bucket_name,
        Key=key,
        Body=json.dumps(raw_data, indent=2),
        ContentType="application/json"
    )

    return f"s3://{bucket_name}/{key}"


def save_jobs_to_dynamodb(dynamodb_table, raw_jobs):
    """
    Parses raw jobs and saves to DynamoDB.
    Same logic as src/services/job_service.py.
    """
    inserted = 0
    skipped = 0

    for item in raw_jobs:
        external_id = str(item.get("id"))

        # Check if job already exists
        existing = dynamodb_table.get_item(
            Key={"external_id": external_id, "source": "adzuna"}
        )

        if "Item" in existing:
            skipped += 1
            continue

        dynamodb_table.put_item(Item={
            "external_id": external_id,
            "source": "adzuna",
            "title": item.get("title", ""),
            "company": (item.get("company") or {}).get("display_name", ""),
            "location": (item.get("location") or {}).get("display_name", ""),
            "description": item.get("description", ""),
        })
        inserted += 1

    return inserted, skipped


def handler(event, context):
    """
    Lambda entry point. AWS calls this function when the Lambda is triggered.

    Parameters:
    - event: dict with input data (from EventBridge, API Gateway, etc.)
      Example: {"what": "python developer", "country": "gb"}
    - context: AWS metadata (request id, time remaining, etc.)
      We don't use it but Lambda always passes it.

    Returns:
    - dict with results (Lambda converts this to JSON automatically)
    """
    # Read search parameters from the event, with defaults.
    what = event.get("what", "python developer")
    country = event.get("country", "gb")

    # Create AWS clients.
    # On Lambda, boto3 automatically uses the IAM Role (no credentials needed).
    s3_client = boto3.client("s3")
    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table(os.getenv("DYNAMODB_TABLE_NAME"))

    # 1. Fetch jobs from Adzuna
    print(f"Fetching jobs for '{what}' in '{country}'...")
    raw_jobs = get_adzuna_jobs(what=what, country=country)
    print(f"Fetched {len(raw_jobs)} jobs")

    # 2. Save raw data to S3
    s3_path = save_raw_to_s3(s3_client, raw_jobs, source="adzuna", search_term=what)
    print(f"Saved raw data to {s3_path}")

    # 3. Save parsed jobs to DynamoDB
    inserted, skipped = save_jobs_to_dynamodb(table, raw_jobs)
    print(f"Inserted: {inserted}, Skipped: {skipped}")

    # Return results.
    # print() outputs go to CloudWatch Logs (AWS logging service).
    return {
        "statusCode": 200,
        "body": {
            "fetched": len(raw_jobs),
            "inserted": inserted,
            "skipped": skipped,
            "s3_path": s3_path,
        }
    }