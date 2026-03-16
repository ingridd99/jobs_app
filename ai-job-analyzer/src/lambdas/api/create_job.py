import boto3
import json
import os


def handler(event, context):
    """
    Creates a single job in DynamoDB.
    API Gateway calls this when it receives: POST /jobs
    
    Request body (JSON string):
    {
        "external_id": "123",
        "source": "manual",
        "title": "Python Developer",
        "company": "Acme",
        "location": "London",
        "description": "..."
    }
    
    event["body"] contains the request body as a STRING.
    We must parse it with json.loads() to get a dict.
    """
    # Parse the request body.
    # API Gateway sends the body as a string, so we convert it to dict.
    try:
        body = json.loads(event.get("body") or "{}")
    except json.JSONDecodeError:
        # Return 400 Bad Request if body is not valid JSON.
        return {
            "statusCode": 400,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": "Invalid JSON body"})
        }

    # Validate required fields.
    required_fields = ["external_id", "source", "title"]
    for field in required_fields:
        if field not in body:
            return {
                "statusCode": 400,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": f"Missing required field: {field}"})
            }

    # Connect to DynamoDB.
    dynamodb = boto3.resource("dynamodb", region_name=os.getenv("AWS_REGION", "us-east-1"))
    table = dynamodb.Table(os.getenv("DYNAMODB_TABLE_NAME"))

    # Build the item to save.
    item = {
        "external_id": body["external_id"],
        "source": body["source"],
        "title": body["title"],
        "company": body.get("company", ""),
        "location": body.get("location", ""),
        "description": body.get("description", ""),
    }

    # Save to DynamoDB.
    table.put_item(Item=item)

    return {
        "statusCode": 201,  # 201 = Created (more specific than 200)
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*"
        },
        "body": json.dumps({"message": "Job created", "job": item})
    }