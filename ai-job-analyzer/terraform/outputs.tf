# After "terraform apply", this prints the table name.
# Useful so your Python app knows the exact name.
output "dynamodb_table_name" {
  description = "The name of the DynamoDB jobs table"
  value       = aws_dynamodb_table.jobs.name
}

# Also output the table ARN (Amazon Resource Name).
# ARN is a unique identifier for any AWS resource.
# You'll need it later for IAM permissions (e.g., Lambda needs access to this table).
output "dynamodb_table_arn" {
  description = "The ARN of the DynamoDB jobs table"
  value       = aws_dynamodb_table.jobs.arn
}