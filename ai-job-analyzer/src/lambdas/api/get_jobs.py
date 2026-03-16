import boto3
import json
import os
from decimal import Decimal


def decimal_to_int(obj):
    """
    DynamoDB returns numbers as Decimal type (not int/float).
    JSON serializer doesn't know how to handle Decimal, so we convert it.
    This is a common gotcha when working with DynamoDB + JSON.
    """
    if isinstance(obj, Decimal):
        return int(obj)
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")


def handler(event, context):
    """
    Returns a list of jobs from DynamoDB.
    API Gateway calls this when it receives: GET /jobs
    
    Query parameters (optional):
    - limit: max number of jobs to return (default: 20)
    
    Example request: GET /jobs?limit=50
    event["queryStringParameters"] = {"limit": "50"}
    """
    # Get query parameters from the request.
    # event["queryStringParameters"] contains URL params like ?limit=50
    # It can be None if no params provided, so we use "or {}"
    query_params = event.get("queryStringParameters") or {}

    # Get the limit param, default to 20 if not provided.
    # Note: query params are always STRINGS in API Gateway, so we convert to int.
    limit = int(query_params.get("limit", 20))

    # Connect to DynamoDB — same as before.
    # On Lambda, boto3 uses IAM Role automatically (no credentials needed).
    dynamodb = boto3.resource("dynamodb", region_name=os.getenv("AWS_REGION", "us-east-1"))
    table = dynamodb.Table(os.getenv("DYNAMODB_TABLE_NAME"))

    # Scan the table with limit.
    response = table.scan(Limit=limit)
    jobs = response.get("Items", [])

    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*"
        },
        # json.dumps converts dict to string (required by API Gateway).
        # default=decimal_to_int handles DynamoDB Decimal types.
        "body": json.dumps({"count": len(jobs), "jobs": jobs}, default=decimal_to_int)
    }