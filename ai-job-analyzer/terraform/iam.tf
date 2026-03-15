#------------
# Problem: Lambda runs in AWS. But by default it has ZERO permissions.
#          It can't read DynamoDB, can't write to S3, can't even log.

# Solution: Create a "role" — like a badge that says what Lambda is allowed to do.
# Job position: "lambda_role"
# Who can have this job: Only Lambda
#-------------
# IAM Role for Lambda.
# A "role" is like an identity that Lambda assumes to get permissions.
# Think of it as: "When Lambda runs, it pretends to be this role."
resource "aws_iam_role" "lambda_role" {
  name = "${var.project_name}-lambda-role-${var.environment}"

  # "assume_role_policy" defines WHO can use this role.
  # Here we say: "Only Lambda service can assume this role."
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "lambda.amazonaws.com"
      }
    }]
  })

  tags = {
    Project     = var.project_name
    Environment = var.environment
  }
}

#----------
# The role exists, but it has no permissions yet.
# The policy says WHAT the role is allowed to do.
#-----------

# Policy: What the Lambda is ALLOWED to do.
# We give it access to DynamoDB, S3, and CloudWatch Logs.
resource "aws_iam_role_policy" "lambda_policy" {
  name = "${var.project_name}-lambda-policy-${var.environment}"
  role = aws_iam_role.lambda_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        # Allow Lambda to read/write our DynamoDB table
        Effect = "Allow"
        Action = [
          "dynamodb:PutItem",
          "dynamodb:GetItem",
          "dynamodb:Scan",
          "dynamodb:Query"
        ]
        # Only this specific table — not all tables (least privilege)
        Resource = aws_dynamodb_table.jobs.arn
      },
      {
        # Allow Lambda to write to our S3 bucket
        Effect = "Allow"
        Action = [
          "s3:PutObject"
        ]
        # "/*" means all files inside the bucket
        Resource = "${aws_s3_bucket.data_lake.arn}/*"
      },
      {
        # Allow Lambda to write logs to CloudWatch
        # CloudWatch is AWS's logging service — like print() but in the cloud
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "arn:aws:logs:*:*:*"
      }
    ]
  })
}