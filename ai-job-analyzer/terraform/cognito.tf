# ─────────────────────────────────────────────────────────────────
# COGNITO USER POOL
# ─────────────────────────────────────────────────────────────────
# A "User Pool" is a database of users.
# Each user has a username, password, and email.
# Cognito handles all password hashing, storage, and security.
#
# Think of it like a "user table" but managed by AWS — you don't
# need to write login/signup code, password reset logic, etc.

resource "aws_cognito_user_pool" "main" {
  # Name of the user pool (appears in AWS Console)
  name = "${var.project_name}-user-pool-${var.environment}"

  # ─────────────────────────────────────────────────────────────
  # PASSWORD POLICY
  # ─────────────────────────────────────────────────────────────
  # Define password requirements for users.
  password_policy {
    minimum_length    = 8           # Min 8 characters
    require_lowercase = true        # Must have a-z
    require_uppercase = true        # Must have A-Z
    require_numbers   = true        # Must have 0-9
    require_symbols   = false       # Don't require special chars (!@#$%)
  }

  # ─────────────────────────────────────────────────────────────
  # AUTO-VERIFIED ATTRIBUTES
  # ─────────────────────────────────────────────────────────────
  # "auto_verified_attributes" = attributes that don't need verification.
  # If we DON'T include "email" here, users must verify their email
  # before they can log in.
  #
  # For development, auto-verify email. For production, require
  # email verification (security best practice).
  auto_verified_attributes = ["email"]

  # ─────────────────────────────────────────────────────────────
  # USERNAME ATTRIBUTES
  # ─────────────────────────────────────────────────────────────
  # Which attributes can be used to log in?
  # "email" = users can log in with their email address.
  username_attributes = ["email"]

  # ─────────────────────────────────────────────────────────────
  # ACCOUNT RECOVERY SETTINGS
  # ─────────────────────────────────────────────────────────────
  # How should users recover their account if they forget their password?
  account_recovery_setting {
    recovery_mechanism {
      # Recovery via email link (most common)
      name     = "verified_email"
      priority = 1
    }
  }

  tags = {
    Project     = var.project_name
    Environment = var.environment
  }
}

# ─────────────────────────────────────────────────────────────────
# COGNITO USER POOL CLIENT
# ─────────────────────────────────────────────────────────────────
# A "Client" is an application that talks to the user pool.
# In our case, it's the frontend (or Bruno during testing).
#
# The client has:
# - client_id: public ID (safe to show to users)
# - client_secret: private key (keep secret, don't expose to frontend)
#
# The frontend uses client_id to call Cognito's auth endpoints.

resource "aws_cognito_user_pool_client" "main" {
  # Name of the client
  name = "${var.project_name}-client-${var.environment}"

  # Which user pool does this client belong to?
  user_pool_id = aws_cognito_user_pool.main.id

  # ─────────────────────────────────────────────────────────────
  # AUTH FLOWS
  # ─────────────────────────────────────────────────────────────
  # "ALLOW_USER_PASSWORD_AUTH" = allow "username + password" login.
  # This is simple but less secure (password is sent to server).
  #
  # More secure: OAuth 2.0 flow (user logs in via browser, gets code,
  # trades code for token). But that's more complex.
  #
  # For this project, we'll use USER_PASSWORD_AUTH for simplicity.
  explicit_auth_flows = [
    "ALLOW_USER_PASSWORD_AUTH",      # username + password
    "ALLOW_REFRESH_TOKEN_AUTH"       # use refresh token to get new access token
  ]


  # ─────────────────────────────────────────────────────────────
  # PREVENT USER EXISTENCE ERRORS
  # ─────────────────────────────────────────────────────────────
  # When a user tries to log in with a non-existent email,
  # should Cognito say "user not found" or "invalid password"?
  #
  # Security best practice: say "invalid password" (same message
  # for both cases) so attackers can't enumerate valid emails.
  prevent_user_existence_errors = "ENABLED"

}

# ─────────────────────────────────────────────────────────────────
# COGNITO AUTHORIZER FOR API GATEWAY
# ─────────────────────────────────────────────────────────────────
# An "Authorizer" is a gatekeeper for API Gateway.
# It says: "Before calling Lambda, check if the request has a valid
# JWT token from Cognito."
#
# Flow:
# 1. User logs in → Cognito returns JWT token
# 2. User calls API with: Authorization: Bearer {token}
# 3. API Gateway → Cognito Authorizer → "Is this token valid?"
# 4. If valid → call Lambda
# 5. If invalid → return 401 Unauthorized

resource "aws_api_gateway_authorizer" "cognito" {
  # Name in API Gateway Console
  name = "${var.project_name}-cognito-authorizer-${var.environment}"

  # Which REST API does this authorizer protect?
  rest_api_id = aws_api_gateway_rest_api.job_analyzer.id

  # Type of authorizer: "COGNITO_USER_POOLS" = use a Cognito user pool
  type = "COGNITO_USER_POOLS"

  # Which Cognito user pool to use?
  provider_arns = [aws_cognito_user_pool.main.arn]

  # Which header contains the JWT token?
  # Standard: "Authorization" header (format: "Bearer {token}")
  identity_source = "method.request.header.Authorization"

  # Cache the auth result for 5 minutes (for performance).
  # If the same token is used multiple times, don't revalidate it each time.
  authorizer_result_ttl_in_seconds = 300
}