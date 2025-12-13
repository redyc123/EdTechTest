from datetime import datetime, timedelta
import secrets
from fastapi import APIRouter, HTTPException

from common.auth.models.requests import GenerateTokenRequest
from common.auth.models.responses import GenerateTokenResponse
from common.auth.tokendata import TokenData
from common.constants import SECRET_TOKEN
from common.auth.auth import valid_tokens


auth_router = APIRouter(tags=["AUTH"])

@auth_router.post("/generate-token",
                 summary="Генерация токена доступа",
                 description="Генерация нового временного токена доступа с использованием секретного токена")
async def generate_token(request: GenerateTokenRequest):
    """
    Генерация нового токена доступа с использованием секретного токена.
    Секретный токен должен быть передан в теле запроса.

    Args:
        request: Объект запроса, содержащий секретный токен

    Returns:
        GenerateTokenResponse: Объект с новым токеном доступа и временем истечения

    Raises:
        HTTPException: Если переданный секретный токен недействителен (код 401)
    """
    global valid_tokens
    if request.secret_token != SECRET_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid secret token")

    # Generate a new token
    access_token = secrets.token_urlsafe(32)
    expires_at = datetime.utcnow() + timedelta(hours=24)  # Token expires in 24 hours

    # Store the token
    token_data = TokenData(token=access_token, expires_at=expires_at)
    valid_tokens.append(token_data)
    print(valid_tokens)
    return GenerateTokenResponse(
        access_token=access_token,
        expires_at=expires_at.isoformat()
    )
