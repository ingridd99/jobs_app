# ─────────────────────────────────────────────
# 1. THE API
# ─────────────────────────────────────────────

# This creates the API Gateway REST API.
# Think of it as the "entry point" — the base URL for all your endpoints.
resource "aws_api_gateway_rest_api" "job_analyzer" {
  name        = "${var.project_name}-api-${var.environment}"
  description = "Job Analyzer API"

  tags = {
    Project     = var.project_name
    Environment = var.environment
  }
}

# ─────────────────────────────────────────────
# 2. THE LAMBDA FUNCTIONS
# ─────────────────────────────────────────────

# Lambda for GET /health
resource "aws_lambda_function" "health" {
  function_name    = "${var.project_name}-health-${var.environment}"
  filename         = "${path.module}/../src/lambdas/api/lambda_function.zip"
  handler          = "health.handler"       # health.py → handler()
  runtime          = "python3.9"
  role             = aws_iam_role.lambda_role.arn
  source_code_hash = filebase64sha256("${path.module}/../src/lambdas/api/lambda_function.zip")

  environment {
    variables = {
      DYNAMODB_TABLE_NAME = aws_dynamodb_table.jobs.name
      AWS_REGION_NAME     = var.aws_region
    }
  }

  tags = {
    Project     = var.project_name
    Environment = var.environment
  }
}

# Lambda for GET /jobs
resource "aws_lambda_function" "get_jobs" {
  function_name    = "${var.project_name}-get-jobs-${var.environment}"
  filename         = "${path.module}/../src/lambdas/api/lambda_function.zip"
  handler          = "get_jobs.handler"     # get_jobs.py → handler()
  runtime          = "python3.9"
  role             = aws_iam_role.lambda_role.arn
  source_code_hash = filebase64sha256("${path.module}/../src/lambdas/api/lambda_function.zip")

  environment {
    variables = {
      DYNAMODB_TABLE_NAME = aws_dynamodb_table.jobs.name
      AWS_REGION_NAME     = var.aws_region
    }
  }

  tags = {
    Project     = var.project_name
    Environment = var.environment
  }
}

# Lambda for POST /jobs
resource "aws_lambda_function" "create_job" {
  function_name    = "${var.project_name}-create-job-${var.environment}"
  filename         = "${path.module}/../src/lambdas/api/lambda_function.zip"
  handler          = "create_job.handler"   # create_job.py → handler()
  runtime          = "python3.9"
  role             = aws_iam_role.lambda_role.arn
  source_code_hash = filebase64sha256("${path.module}/../src/lambdas/api/lambda_function.zip")

  environment {
    variables = {
      DYNAMODB_TABLE_NAME = aws_dynamodb_table.jobs.name
      AWS_REGION_NAME     = var.aws_region
    }
  }

  tags = {
    Project     = var.project_name
    Environment = var.environment
  }
}

# Lambda for GET /analytics/skills
resource "aws_lambda_function" "analytics" {
  function_name    = "${var.project_name}-analytics-${var.environment}"
  filename         = "${path.module}/../src/lambdas/api/lambda_function.zip"
  handler          = "analytics.handler"    # analytics.py → handler()
  runtime          = "python3.9"
  role             = aws_iam_role.lambda_role.arn
  source_code_hash = filebase64sha256("${path.module}/../src/lambdas/api/lambda_function.zip")

  environment {
    variables = {
      DYNAMODB_TABLE_NAME = aws_dynamodb_table.jobs.name
      AWS_REGION_NAME     = var.aws_region
    }
  }

  tags = {
    Project     = var.project_name
    Environment = var.environment
  }
}

# ─────────────────────────────────────────────
# 3. THE ROUTES (Resources + Methods)
# ─────────────────────────────────────────────
# In API Gateway, a "resource" is a URL path segment.
# A "method" is an HTTP verb (GET, POST, etc.) on that resource.

# /health resource
resource "aws_api_gateway_resource" "health" {
  rest_api_id = aws_api_gateway_rest_api.job_analyzer.id
  parent_id   = aws_api_gateway_rest_api.job_analyzer.root_resource_id
  # "path_part" is the URL segment: /health
  path_part   = "health"
}

# GET /health method
resource "aws_api_gateway_method" "health_get" {
  rest_api_id   = aws_api_gateway_rest_api.job_analyzer.id
  resource_id   = aws_api_gateway_resource.health.id
  http_method   = "GET"
  # "NONE" means no authentication required (we'll change this in Step 5 with Cognito)
  authorization = "NONE"
}

# /jobs resource
resource "aws_api_gateway_resource" "jobs" {
  rest_api_id = aws_api_gateway_rest_api.job_analyzer.id
  parent_id   = aws_api_gateway_rest_api.job_analyzer.root_resource_id
  path_part   = "jobs"
}

# GET /jobs method
resource "aws_api_gateway_method" "jobs_get" {
  rest_api_id   = aws_api_gateway_rest_api.job_analyzer.id
  resource_id   = aws_api_gateway_resource.jobs.id
  http_method   = "GET"
  # Require Cognito authentication
  authorization = "COGNITO_USER_POOLS"
  # Use our Cognito authorizer
  authorizer_id = aws_api_gateway_authorizer.cognito.id
  
  # Tell API Gateway that Authorization header is required
  request_parameters = {
    "method.request.header.Authorization" = true
  }
}

# POST /jobs method
resource "aws_api_gateway_method" "jobs_post" {
  rest_api_id   = aws_api_gateway_rest_api.job_analyzer.id
  resource_id   = aws_api_gateway_resource.jobs.id
  http_method   = "POST"
  # Require Cognito authentication
  authorization = "COGNITO_USER_POOLS"
  # Use our Cognito authorizer
  authorizer_id = aws_api_gateway_authorizer.cognito.id
  
  # Tell API Gateway that Authorization header is required
  request_parameters = {
    "method.request.header.Authorization" = true
  }
}

# /analytics resource
resource "aws_api_gateway_resource" "analytics" {
  rest_api_id = aws_api_gateway_rest_api.job_analyzer.id
  parent_id   = aws_api_gateway_rest_api.job_analyzer.root_resource_id
  path_part   = "analytics"
}

# /analytics/skills resource (nested under /analytics)
resource "aws_api_gateway_resource" "analytics_skills" {
  rest_api_id = aws_api_gateway_rest_api.job_analyzer.id
  # parent_id points to /analytics — making this /analytics/skills
  parent_id   = aws_api_gateway_resource.analytics.id
  path_part   = "skills"
}

# GET /analytics/skills method
resource "aws_api_gateway_method" "analytics_skills_get" {
  rest_api_id   = aws_api_gateway_rest_api.job_analyzer.id
  resource_id   = aws_api_gateway_resource.analytics_skills.id
  http_method   = "GET"
  # Require Cognito authentication
  authorization = "COGNITO_USER_POOLS"
  # Use our Cognito authorizer
  authorizer_id = aws_api_gateway_authorizer.cognito.id

  # Tell API Gateway that Authorization header is required
  request_parameters = {
    "method.request.header.Authorization" = true
    }
}

# ─────────────────────────────────────────────
# 4. INTEGRATIONS (Connect routes to Lambdas)
# ─────────────────────────────────────────────
# An "integration" connects a route+method to a Lambda function.
# "AWS_PROXY" means API Gateway passes the full request to Lambda
# and Lambda is responsible for the full response.

# GET /health → health Lambda
resource "aws_api_gateway_integration" "health_get" {
  rest_api_id             = aws_api_gateway_rest_api.job_analyzer.id
  resource_id             = aws_api_gateway_resource.health.id
  http_method             = aws_api_gateway_method.health_get.http_method
  integration_http_method = "POST"  # Lambda invocation always uses POST internally
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.health.invoke_arn
}

# GET /jobs → get_jobs Lambda
resource "aws_api_gateway_integration" "jobs_get" {
  rest_api_id             = aws_api_gateway_rest_api.job_analyzer.id
  resource_id             = aws_api_gateway_resource.jobs.id
  http_method             = aws_api_gateway_method.jobs_get.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.get_jobs.invoke_arn
}

# POST /jobs → create_job Lambda
resource "aws_api_gateway_integration" "jobs_post" {
  rest_api_id             = aws_api_gateway_rest_api.job_analyzer.id
  resource_id             = aws_api_gateway_resource.jobs.id
  http_method             = aws_api_gateway_method.jobs_post.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.create_job.invoke_arn
}

# GET /analytics/skills → analytics Lambda
resource "aws_api_gateway_integration" "analytics_skills_get" {
  rest_api_id             = aws_api_gateway_rest_api.job_analyzer.id
  resource_id             = aws_api_gateway_resource.analytics_skills.id
  http_method             = aws_api_gateway_method.analytics_skills_get.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.analytics.invoke_arn
}

# ─────────────────────────────────────────────
# 5. PERMISSIONS (Allow API Gateway to invoke Lambdas)
# ─────────────────────────────────────────────
# Without these, API Gateway would get "Access Denied" when calling Lambda.

resource "aws_lambda_permission" "health_api" {
  statement_id  = "AllowAPIGatewayHealth"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.health.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.job_analyzer.execution_arn}/*/*"
}

resource "aws_lambda_permission" "get_jobs_api" {
  statement_id  = "AllowAPIGatewayGetJobs"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.get_jobs.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.job_analyzer.execution_arn}/*/*"
}

resource "aws_lambda_permission" "create_job_api" {
  statement_id  = "AllowAPIGatewayCreateJob"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.create_job.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.job_analyzer.execution_arn}/*/*"
}

resource "aws_lambda_permission" "analytics_api" {
  statement_id  = "AllowAPIGatewayAnalytics"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.analytics.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.job_analyzer.execution_arn}/*/*"
}

# ─────────────────────────────────────────────
# 6. DEPLOYMENT
# ─────────────────────────────────────────────
# A "deployment" is a snapshot of the API configuration.
# You must deploy the API for changes to take effect.
# Think of it like "publishing" your API.

resource "aws_api_gateway_deployment" "job_analyzer" {
  rest_api_id = aws_api_gateway_rest_api.job_analyzer.id

  # This tells Terraform to redeploy when any method or integration changes.
  # Without this, changes to routes wouldn't trigger a new deployment.
  triggers = {
    redeployment = sha1(jsonencode([
      aws_api_gateway_method.health_get,
      aws_api_gateway_method.jobs_get,
      aws_api_gateway_method.jobs_post,
      aws_api_gateway_method.analytics_skills_get,
      aws_api_gateway_integration.health_get,
      aws_api_gateway_integration.jobs_get,
      aws_api_gateway_integration.jobs_post,
      aws_api_gateway_integration.analytics_skills_get,
    ]))
  }

  # Ensures deployment happens AFTER all integrations are created.
  depends_on = [
    aws_api_gateway_integration.health_get,
    aws_api_gateway_integration.jobs_get,
    aws_api_gateway_integration.jobs_post,
    aws_api_gateway_integration.analytics_skills_get,
  ]
}

# ─────────────────────────────────────────────
# 7. STAGE
# ─────────────────────────────────────────────
# A "stage" is a named version of your API deployment.
# Common stages: dev, staging, prod.
# The stage name becomes part of the URL:
#   https://{api-id}.execute-api.us-east-1.amazonaws.com/{stage}/health

resource "aws_api_gateway_stage" "job_analyzer" {
  deployment_id = aws_api_gateway_deployment.job_analyzer.id
  rest_api_id   = aws_api_gateway_rest_api.job_analyzer.id
  stage_name    = var.environment

  # Add this line — it tells Terraform to update/recreate the stage
  # whenever the deployment changes, preventing orphaned deployments.
  lifecycle {
    create_before_destroy = true
  }

  tags = {
    Project     = var.project_name
    Environment = var.environment
  }
}