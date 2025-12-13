from datetime import datetime
from fastapi import HTTPException, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

valid_tokens = []

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer(auto_error=False))):
    """Get current user by checking the token in Authorization header or query parameter"""
    token = None

    # Check authorization header
    if credentials:
        token = credentials.credentials
    else:
        # Check query parameter (for cases where header isn't accessible)
        token = None  # Will be retrieved from request later

    return token

def verify_token(token: str, valid_tokens: list) -> bool:
    """Check if the token is valid and not expired"""
    # Remove expired tokens
    current_time = datetime.now()
    print("1", valid_tokens)
    valid_tokens = [
        t for t in valid_tokens 
        if t.expires_at > current_time
    ]
    print("2", valid_tokens)
    # Check if the token exists in valid_tokens
    for token_data in valid_tokens:
        if token_data.token == token:
            return True
    return False

def require_valid_token(request: Request, token: str = Depends(get_current_user)):
    """Dependency that checks for a valid token in header or query param"""
    # If token is not in header, check query parameter
    if not token:
        token = request.query_params.get('token', "")

    if not token or not verify_token(token, valid_tokens):
        raise HTTPException(
            status_code=401,
            detail="Invalid or missing token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return token