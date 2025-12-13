import asyncio
from uuid import UUID
from fastapi import APIRouter, Depends, File, UploadFile
from api.models.requests import AddDocumentsRequest, RemoveDocumentsRequest
from common.auth.auth import require_valid_token
from api.utils.vectorstore import create_vectorstore
from api.models.responses import AddDocumentsResponse
from api.utils.parser import (
    convert_file_async,
    get_result_task_convert
)
from api.utils.splitter import split_text, create_splitter

vectorstore_router = APIRouter(tags=["VECTORSTORE"], dependencies=[Depends(require_valid_token)])

@vectorstore_router.post("/v1/remove/documents",
                        summary="Удаление документов из векторного хранилища",
                        description="Удаление документов по их идентификаторам из векторного хранилища диалога")
async def remove_documents(request: RemoveDocumentsRequest):
    """
    Удаление документов из векторного хранилища по списку идентификаторов.

    Args:
        request: Объект запроса, содержащий идентификатор диалога и список идентификаторов документов для удаления
    """
    vectorstore = create_vectorstore(str(request.dialog_id))
    await vectorstore.adelete(request.ids)

@vectorstore_router.post("/v1/parse/document",
                        summary="Парсинг и добавление документа",
                        description="Загрузка документа, его парсинг и добавление в векторное хранилище")
async def parse_document(dialog_id: UUID, file: UploadFile = File()) -> AddDocumentsResponse:
    """
    Загрузка и парсинг документа с последующим добавлением в векторное хранилище.

    Args:
        dialog_id: Идентификатор диалога, в котором будет храниться документ
        file: Загружаемый документ

    Returns:
        AddDocumentsResponse: Объект с идентификаторами добавленных документов

    Raises:
        Exception: Если не удалось создать задачу на парсинг
    """
    task_id = await convert_file_async(file.file.read(), file.filename)
    if not task_id:
        raise Exception("NOT TASK ID")
    task_complited = None
    while not task_complited:
        task_complited = await get_result_task_convert(task_id)
        await asyncio.sleep(10)
    text, filename = task_complited
    vectorstore = create_vectorstore(str(dialog_id))
    splitter = create_splitter()
    documents = await split_text(text, splitter, source=filename)
    return AddDocumentsResponse(
        ids=await vectorstore.aadd_documents(documents)
    )