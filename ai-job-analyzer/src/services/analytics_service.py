from src.db.dynamodb import get_dynamodb_table

# The skills we want to search for in job descriptions.
SKILL_KEYWORDS = [
    "python", "java", "javascript", "typescript", "aws", "docker",
    "kubernetes", "react", "sql", "terraform", "go", "rust",
    "node", "angular", "azure", "gcp", "linux", "git",
]

table = get_dynamodb_table()

def get_skill_counts() -> list:
    """
    Counts how many jobs mention each skill in their title or description.

    We scan ALL jobs and check each one against our keyword list.

    In PostgreSQL we used SQL LIKE queries.
    In DynamoDB there's no full-text search, so we do it in Python.
    (Later, we'll use Athena for proper SQL analytics over S3 data.)
    """

    # Scan all items — for analytics we need to look at every job.
    # We only fetch the fields we need (ProjectionExpression) to save bandwidth.
    response = table.scan(
        # Only return title and description fields, not all fields.
        ProjectionExpression="title, description"
    )
    items = response.get("Items", [])

    # DynamoDB scan() returns max 1MB of data per call.
    # If there's more data, it returns a "LastEvaluatedKey" and we must call again.
    # This loop handles pagination — it keeps scanning until all items are read.
    while "LastEvaluatedKey" in response:
        response = table.scan(
            ProjectionExpression="title, description",
            ExclusiveStartKey=response["LastEvaluatedKey"]
        )
        items.extend(response.get("Items", []))

    # Count each skill keyword across all jobs.
    skill_counts = {}
    for skill in SKILL_KEYWORDS:
        skill_counts[skill] = 0
        for item in items:
            text = (item.get("title", "") + " " + item.get("description", "")).lower()
            if skill in text:
                skill_counts[skill] += 1

    # Return as a sorted list of dicts — most mentioned skills first.
    result = [{"skill": skill, "count": count} for skill, count in skill_counts.items()]
    result.sort(key=lambda x: x["count"], reverse=True)

    return result