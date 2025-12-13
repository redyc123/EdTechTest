from uuid import UUID
from fastapi import File, UploadFile
from pydantic import BaseModel
from langchain_core.documents import Document

class Base(BaseModel):
    """Базовая модель, содержащая идентификатор диалога"""
    dialog_id: UUID

class TextCompletionRequest(Base):
    """Модель запроса для текстового завершения"""
    query: str = ""

class AddDocumentsRequest(Base):
    """Модель запроса для добавления документов"""
    documents: list[Document]

class RemoveDocumentsRequest(Base):
    """Модель запроса для удаления документов по идентификаторам"""
    ids: list[str]