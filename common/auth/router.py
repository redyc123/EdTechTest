from datetime import datetime, timedelta
import secrets
from fastapi import APIRouter, HTTPException

from common.auth.models.requests import GenerateTokenRequest
from common.auth.models.responses import GenerateTokenResponse
from common.auth.tokendata import TokenData
from common.constants import SECRET_TOKEN
from common.auth.auth import valid_tokens


auth_router = APIRouter(tags=["AUTH"])

@auth_router.post("/generate-token")
async def generate_token(request: GenerateTokenRequest):
    """
    Generate a new access token using the secret token.
    The secret token should be passed in the request body.
    """
    if request.secret_token != SECRET_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid secret token")
    
    # Generate a new token
    access_token = secrets.token_urlsafe(32)
    expires_at = datetime.utcnow() + timedelta(hours=24)  # Token expires in 24 hours
    
    # Store the token
    token_data = TokenData(token=access_token, expires_at=expires_at)
    valid_tokens.append(token_data)
    
    return GenerateTokenResponse(
        access_token=access_token,
        expires_at=expires_at.isoformat()
    )
