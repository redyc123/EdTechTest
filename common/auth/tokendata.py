from datetime import datetime


class TokenData:
    def __init__(self, token: str, expires_at: datetime):
        self.token = token
        self.expires_at = expires_at