from pydantic import BaseModel


class GenerateTokenResponse(BaseModel):
    """Модель ответа при генерации токена доступа"""
    access_token: str
    expires_at: str