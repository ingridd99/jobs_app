# This creates a DynamoDB table in AWS.
# DynamoDB is a NoSQL database — instead of rows/columns like PostgreSQL,
# it stores "items" (like JSON documents).
resource "aws_dynamodb_table" "jobs" {

  # The actual table name in AWS.
  # "${var.project_name}" and "${var.environment}" are variable interpolations.
  # Result: "job-analyzer-jobs-dev"
  name = "${var.project_name}-jobs-${var.environment}"

  # Billing mode — how you pay for DynamoDB.
  # "PAY_PER_REQUEST" = you pay only for what you use (no capacity planning).
  # The alternative is "PROVISIONED" where you pre-set read/write capacity.
  # PAY_PER_REQUEST is perfect for dev/learning — no cost if no traffic.
  billing_mode = "PAY_PER_REQUEST"

  # The "hash_key" is the PARTITION KEY — the primary way DynamoDB finds items.
  # Think of it like the PRIMARY KEY in PostgreSQL.
  # Each job from Adzuna has a unique "external_id", so we use that.
  hash_key = "external_id"

  # The "range_key" is the SORT KEY — it's the second part of the primary key.
  # Together, hash_key + range_key must be unique.
  # We use "source" (e.g., "adzuna") so the same external_id from
  # different sources (adzuna, linkedin, etc.) won't conflict.
  range_key = "source"

  # We must declare the TYPE of each key attribute.
  # "S" = String, "N" = Number, "B" = Binary.
  # NOTE: You only define attributes here that are used as keys or indexes.
  # Other fields (title, company, etc.) are added freely in your Python code.
  attribute {
    name = "external_id"
    type = "S"
  }

  attribute {
    name = "source"
    type = "S"
  }

  # Tags are metadata labels for the resource.
  # They help you organize, search, and track costs in AWS.
  tags = {
    Project     = var.project_name
    Environment = var.environment
  }
}