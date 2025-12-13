from pydantic import BaseModel

class AddDocumentsResponse(BaseModel):
    """Модель ответа при добавлении документов, содержащая идентификаторы добавленных документов"""
    ids: list[str]