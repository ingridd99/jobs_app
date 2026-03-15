# An S3 bucket is like a folder in the cloud that stores files (called "objects").
# We'll use it as a "data lake" — a place to store ALL raw data.
resource "aws_s3_bucket" "data_lake" {

  # Bucket name must be globally unique across ALL AWS accounts worldwide.
  # That's why we include your name to make it unique.
  bucket = "${var.project_name}-data-lake-${var.environment}-ingr"

  tags = {
    Project     = var.project_name
    Environment = var.environment
  }
}

# Enable versioning — keeps old versions of files when you overwrite them.
resource "aws_s3_bucket_versioning" "data_lake" {
  bucket = aws_s3_bucket.data_lake.id

  versioning_configuration {
    status = "Enabled"
  }
}

# Lifecycle rules — automatically move old files to cheaper storage.
resource "aws_s3_bucket_lifecycle_configuration" "data_lake" {
  bucket = aws_s3_bucket.data_lake.id

  rule {
    id     = "archive-old-raw-data"
    status = "Enabled"

    filter {
      prefix = "raw/"
    }

    # After 90 days, move to Glacier (very cheap, slow to retrieve).
    transition {
      days          = 90
      storage_class = "GLACIER"
    }
  }
}