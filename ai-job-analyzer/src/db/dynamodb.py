# boto3 is the AWS SDK for Python.
# It lets you interact with any AWS service (DynamoDB, S3, Lambda, etc.)
import boto3

# We import os to read environment variables.
import os


def get_dynamodb_table():
    """
    Creates a connection to our DynamoDB table and returns the table object.
    This is similar to what 'engine' and 'SessionLocal' did for PostgreSQL —
    it gives us an object we can use to read/write data.
    """

    # boto3.resource() creates a high-level, easy-to-use client.
    # (There's also boto3.client() which is lower-level — more control, more verbose.)
    # It automatically uses the credentials from "aws configure".
    dynamodb = boto3.resource(
        "dynamodb",
        region_name=os.getenv("AWS_REGION", "us-east-1")
    )

    # Get a reference to our specific table.
    # The table name must match what Terraform created: "job-analyzer-jobs-dev"
    table_name = os.getenv("DYNAMODB_TABLE_NAME", "job-analyzer-jobs-dev")
    table = dynamodb.Table(table_name)

    return table