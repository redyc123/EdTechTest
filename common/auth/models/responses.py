from pydantic import BaseModel


class GenerateTokenResponse(BaseModel):
    access_token: str
    expires_at: str