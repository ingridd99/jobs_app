# We import the DynamoDB table instead of the SQLAlchemy session.
from src.db.dynamodb import get_dynamodb_table

# We still use the same Pydantic schema for validation.
from src.schemas.job import JobCreate

from typing import Optional

# boto3 has special exceptions we might need to handle.
from botocore.exceptions import ClientError

# Get the table object — similar to getting a DB session.
table = get_dynamodb_table()

def create_job(job: JobCreate) -> dict:
    """
    Saves a single job to DynamoDB.
    Similar to what we did before with db.add() + db.commit().

    In DynamoDB, we use put_item() which takes a dict (called "Item").
    There's no ORM model — we just pass a dictionary directly.
    """
    item = {
        "external_id": job.external_id,
        "source": job.source,
        "title": job.title,
        "company": job.company or "",
        "location": job.location or "",
        "description": job.description or "",
    }

    # put_item() writes the item to the table.
    # If an item with the same external_id + source already exists,
    # it will be OVERWRITTEN (unlike PostgreSQL which would throw a duplicate error).
    table.put_item(Item=item)

    return item


def get_jobs(limit: int = 20) -> list:
    """
    Retrieves jobs from DynamoDB.

    In PostgreSQL we did: db.query(Job).limit(20).all()
    In DynamoDB we use scan() — it reads ALL items in the table.

    NOTE: scan() is expensive on large tables because it reads everything.
    For production, you'd use query() with a specific key, or add pagination.
    For learning purposes, scan() with a limit is fine.
    """
    response = table.scan(
        # Limit = max number of items to return in one call.
        Limit=limit
    )

    # DynamoDB returns the items under the "Items" key.
    return response.get("Items", [])


def get_job_by_id(external_id: str, source: str = "adzuna") -> Optional[dict]:
    """
    Retrieves a single job by its primary key (external_id + source).

    In PostgreSQL we did: db.query(Job).filter(Job.id == id).first()
    In DynamoDB we use get_item() with the exact key.
    This is VERY fast — O(1) lookup, like a dictionary.
    """
    response = table.get_item(
        Key={
            "external_id": external_id,
            "source": source,
        }
    )

    # If the item exists, it's under "Item". If not, "Item" won't be in the response.
    return response.get("Item")



def ingest_jobs_from_adzuna(what: str = "python developer", country: str = "gb") -> dict:
    """
    Fetches jobs from Adzuna API and saves them to DynamoDB.
    Same logic as before, but writes to DynamoDB instead of PostgreSQL.
    """
    # Import here to avoid circular imports.
    from src.clients.adzuna_client import fetch_adzuna_jobs

    # Fetch raw jobs from Adzuna API.
    raw_jobs = fetch_adzuna_jobs(what=what, country=country)

    inserted = 0
    skipped = 0

    for item in raw_jobs:
        external_id = str(item.get("id"))

        # Check if this job already exists in DynamoDB.
        existing = get_job_by_id(external_id, source="adzuna")

        if existing:
            # Job already in DB — skip it.
            skipped += 1
            continue

        # Create a JobCreate schema to validate the data.
        job = JobCreate(
            external_id=external_id,
            source="adzuna",
            title=item.get("title", ""),
            company=(item.get("company") or {}).get("display_name", ""),
            location=(item.get("location") or {}).get("display_name", ""),
            description=item.get("description", ""),
        )

        # Save to DynamoDB.
        create_job(job)
        inserted += 1

    return {
        "fetched": len(raw_jobs),
        "inserted": inserted,
        "skipped": skipped,
    }