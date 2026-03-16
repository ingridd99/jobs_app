import boto3
import json
import os
from decimal import Decimal

# Skills to search for across all job descriptions.
SKILL_KEYWORDS = [
    "python", "java", "javascript", "typescript", "aws", "docker",
    "kubernetes", "react", "sql", "terraform", "go", "rust",
    "node", "angular", "azure", "gcp", "linux", "git",
]


def decimal_to_int(obj):
    """Convert DynamoDB Decimal to int for JSON serialization."""
    if isinstance(obj, Decimal):
        return int(obj)
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")


def handler(event, context):
    """
    Returns skill counts across all jobs.
    API Gateway calls this when it receives: GET /analytics/skills

    Scans ALL jobs in DynamoDB and counts keyword matches.
    Handles DynamoDB pagination (1MB limit per scan call).
    """
    dynamodb = boto3.resource("dynamodb", region_name=os.getenv("AWS_REGION", "us-east-1"))
    table = dynamodb.Table(os.getenv("DYNAMODB_TABLE_NAME"))

    # Scan all items — only fetch title and description to save bandwidth.
    response = table.scan(
        ProjectionExpression="title, description"
    )
    items = response.get("Items", [])

    # Handle pagination — DynamoDB returns max 1MB per call.
    while "LastEvaluatedKey" in response:
        response = table.scan(
            ProjectionExpression="title, description",
            ExclusiveStartKey=response["LastEvaluatedKey"]
        )
        items.extend(response.get("Items", []))

    # Count skill mentions across all jobs.
    skill_counts = {}
    for skill in SKILL_KEYWORDS:
        skill_counts[skill] = 0
        for item in items:
            text = (item.get("title", "") + " " + item.get("description", "")).lower()
            if skill in text:
                skill_counts[skill] += 1

    # Sort by count descending.
    result = [{"skill": skill, "count": count} for skill, count in skill_counts.items()]
    result.sort(key=lambda x: x["count"], reverse=True)

    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*"
        },
        "body": json.dumps({"skills": result}, default=decimal_to_int)
    }