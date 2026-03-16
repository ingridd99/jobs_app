import boto3
import json
import requests
import os

# Get Cognito credentials from Terraform outputs or env vars
COGNITO_CLIENT_ID = "46jhf2di94it9hob018h5tk5kr"  # from terraform output
# COGNITO_CLIENT_SECRET = "xyz789..."  # from terraform output
COGNITO_REGION = "us-east-1"
API_URL = "https://38v1g116k9.execute-api.us-east-1.amazonaws.com/dev"

# ─────────────────────────────────────────────────────────────
# STEP 1: Authenticate with Cognito
# ─────────────────────────────────────────────────────────────
def authenticate(username: str, password: str) -> str:
    """
    Authenticate with Cognito and get a JWT token.
    
    Returns:
        JWT token (string) to use in API requests
    """
    # Create Cognito client
    cognito = boto3.client("cognito-idp", region_name=COGNITO_REGION)

    # Call InitiateAuth — Cognito's authentication endpoint
    response = cognito.initiate_auth(
        ClientId=COGNITO_CLIENT_ID,
        AuthFlow="USER_PASSWORD_AUTH",  # username + password flow
        AuthParameters={
            "USERNAME": username,
            "PASSWORD": password,
        },
    )

    # Extract the JWT token from the response
    # Cognito returns: {"AuthenticationResult": {"IdToken": "...", ...}}
    token = response["AuthenticationResult"]["IdToken"]
    print(f"✅ Authenticated as {username}")
    print(f"   Token: {token[:50]}...  (truncated)\n")

    return token


# ─────────────────────────────────────────────────────────────
# STEP 2: Call protected API endpoints with token
# ─────────────────────────────────────────────────────────────
def call_protected_api(token: str, method: str, endpoint: str, body: dict = None) -> dict:
    """
    Call a protected API endpoint with the JWT token.
    
    Args:
        token: JWT access token from Cognito
        method: HTTP method (GET, POST)
        endpoint: API endpoint (e.g., "/jobs", "/analytics/skills")
        body: request body for POST requests
    
    Returns:
        Response from the API
    """
    url = f"{API_URL}{endpoint}"

     # Set up headers with Authorization token
    headers = {
        "Authorization": f"Bearer {token}",  # Make sure it's "Bearer {token}"
        "Content-Type": "application/json",
    }

    print(f"Headers being sent: {headers}\n")  # DEBUG: print headers

    # Make the request
    if method == "GET":
        response = requests.get(url, headers=headers)
    elif method == "POST":
        response = requests.post(url, headers=headers, json=body)
    else:
        raise ValueError(f"Unsupported HTTP method: {method}")

    # Print response
    print(f"{method} {endpoint}")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}\n")

    return response.json()


# ─────────────────────────────────────────────────────────────
# STEP 3: Test without token (should fail with 401)
# ─────────────────────────────────────────────────────────────
def test_without_token():
    """
    Try to call protected endpoint WITHOUT token.
    Should get 401 Unauthorized.
    """
    print("─" * 60)
    print("TEST: Call API WITHOUT token (should fail)")
    print("─" * 60 + "\n")

    url = f"{API_URL}/jobs"
    response = requests.get(url)

    print(f"GET {url}")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}\n")

    if response.status_code == 401:
        print("✅ Correctly rejected request without token\n")
    else:
        print("❌ ERROR: Should have returned 401\n")


# ─────────────────────────────────────────────────────────────
# MAIN TEST FLOW
# ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    # Test without token first
    test_without_token()

    # Authenticate
    print("─" * 60)
    print("AUTHENTICATE WITH COGNITO")
    print("─" * 60 + "\n")

    token = authenticate(
        username="testuser@example.com",
        password="MyPassword123!"
    )

    # Call protected endpoints with token
    print("─" * 60)
    print("CALL PROTECTED ENDPOINTS WITH TOKEN")
    print("─" * 60 + "\n")

    # GET /jobs
    call_protected_api(token, "GET", "/jobs?limit=5")

    # GET /analytics/skills
    call_protected_api(token, "GET", "/analytics/skills")

    # POST /jobs
    call_protected_api(token, "POST", "/jobs", {
        "external_id": "test-cognito-1",
        "source": "cognito-test",
        "title": "Cognito Test Job",
        "company": "Test Corp",
        "location": "Testville",
        "description": "Testing Cognito auth"
    })

    print("─" * 60)
    print("✅ ALL TESTS PASSED")
    print("─" * 60)