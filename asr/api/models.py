from datetime import datetime
from pydantic import BaseModel
from typing import Optional

class TranscriptionResponse(BaseModel):
    text: str
    language: str | None = None
    duration: float | None = None


class HealthCheck(BaseModel):
    status: str = "OK"


class GenerateTokenRequest(BaseModel):
    secret_token: str


class GenerateTokenResponse(BaseModel):
    access_token: str
    expires_at: str


class TokenData:
    def __init__(self, token: str, expires_at: datetime):
        self.token = token
        self.expires_at = expires_at