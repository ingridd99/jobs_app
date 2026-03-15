# The Lambda function itself.
resource "aws_lambda_function" "ingest" {
  # Name of the function in AWS
  function_name = "${var.project_name}-ingest-${var.environment}"

  # Path to the zip file we created with build.sh
  filename = "${path.module}/../src/lambda/lambda_function.zip"

  # Tells Lambda: "In the zip, find handler.py and call the function named handler"
  # Format: {filename_without_extension}.{function_name}
  handler = "handler.handler"

  # Python version to use
  runtime = "python3.9"

  # The IAM Role that gives Lambda permissions
  role = aws_iam_role.lambda_role.arn

  # Timeout in seconds. Lambda stops after this time.
  # Default is 3 seconds — too short for API calls. 60 seconds is safer.
  timeout = 60

  # Memory in MB. More memory = faster execution (and more cost).
  # 256 MB is enough for our use case.
  memory_size = 256

  # Environment variables — accessible via os.getenv() in Python.
  # This is how Lambda knows which table and bucket to use.
  environment {
    variables = {
      DYNAMODB_TABLE_NAME = aws_dynamodb_table.jobs.name
      S3_BUCKET_NAME      = aws_s3_bucket.data_lake.id
      ADZUNA_APP_ID       = var.adzuna_app_id
      ADZUNA_APP_KEY      = var.adzuna_app_key
    }
  }

  # This tells Terraform to detect when the zip file changes
  # and update the Lambda function automatically.
  source_code_hash =  filebase64sha256("${path.module}/../src/lambda/lambda_function.zip")

  tags = {
    Project     = var.project_name
    Environment = var.environment
  }
}

# EventBridge rule — triggers the Lambda on a schedule.
# This is like a cron job in the cloud.
resource "aws_cloudwatch_event_rule" "ingest_schedule" {
  name                = "${var.project_name}-ingest-schedule-${var.environment}"
  description         = "Triggers job ingestion every 6 hours"

  # Cron expression: run at minute 0, every 6 hours, every day.
  # Format: cron(minutes hours day-of-month month day-of-week year)
  schedule_expression = "rate(6 hours)"

  tags = {
    Project     = var.project_name
    Environment = var.environment
  }
}

# Connect the EventBridge rule to the Lambda function.
# "When the schedule fires, call this Lambda."
resource "aws_cloudwatch_event_target" "ingest_target" {
  rule = aws_cloudwatch_event_rule.ingest_schedule.name
  arn  = aws_lambda_function.ingest.arn

  # The input passed to the Lambda as the "event" parameter.
  input = jsonencode({
    what    = "python developer"
    country = "gb"
  })
}

# Permission: Allow EventBridge to invoke (call) the Lambda.
# Without this, EventBridge would get "Access Denied".
resource "aws_lambda_permission" "allow_eventbridge" {
  statement_id  = "AllowEventBridge"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.ingest.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.ingest_schedule.arn
}


# Every 6 hours:
                                    
#   EventBridge Rule                  "It's time!"
#        ↓
#   EventBridge Target                "Call Lambda with {what: python developer}"
#        ↓
#   Lambda Permission                 "EventBridge is allowed to call me"
#        ↓
#   Lambda Function                   "Running handler.handler..."
#        ↓
#   IAM Role + Policy                 "I have permission to use DynamoDB + S3"
#        ↓
#   handler(event, context)           "Fetching jobs, saving to S3 + DynamoDB"
#        ↓
#   CloudWatch Logs                   "print() output saved here"