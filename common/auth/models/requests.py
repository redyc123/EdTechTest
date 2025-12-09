from pydantic import BaseModel


class GenerateTokenRequest(BaseModel):
    secret_token: str