from pydantic import BaseModel


class GenerateTokenRequest(BaseModel):
    """Модель запроса для генерации токена доступа"""
    secret_token: str