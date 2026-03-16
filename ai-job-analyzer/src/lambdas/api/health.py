def handler(event, context):
    """
    Health check endpoint.
    API Gateway calls this when it receives: GET /health
    
    event contains:
    - httpMethod: "GET"
    - path: "/health"
    - headers: {...}
    - queryStringParameters: {...}
    - body: "..." (for POST requests)
    
    We must return a dict with:
    - statusCode: HTTP status code (200, 400, 404, 500, etc.)
    - headers: response headers
    - body: response body AS A STRING (not dict — API Gateway requires string)
    """
    return {
        "statusCode": 200,
        "headers": {
            # Allow cross-origin requests (needed for frontend apps)
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*"
        },
        "body": '{"status": "ok"}'
    }