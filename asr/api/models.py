from datetime import datetime
from pydantic import BaseModel
from typing import Optional

class TranscriptionResponse(BaseModel):
    text: str
    language: str | None = None
    duration: float | None = None


class HealthCheck(BaseModel):
    status: str = "OK"