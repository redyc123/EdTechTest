from uuid import UUID
from fastapi import APIRouter, Depends, File, UploadFile
from api.utils.chains import run_llm_pipeline
from api.models.requests import TextCompletionRequest
from langchain_core.messages import AIMessage
from api.utils.asr import ASR
from common.auth.auth import require_valid_token
from api.database.database import clear_chat_history, get_chat_history

chat_router = APIRouter(tags=["LLM"], dependencies=[Depends(require_valid_token)])

@chat_router.post("/v1/chat/completion/text",
                 summary="Обработка текстового запроса",
                 description="Отправка текстового сообщения в чат и получение ответа от языковой модели")
async def text_answer(
    request: TextCompletionRequest = Depends(),
    picture: UploadFile | None = None
) -> AIMessage:
    """
    Отправка текстового запроса и необязательного изображения в чат.

    Args:
        request: Текстовый запрос пользователя и идентификатор диалога
        picture: Необязательное изображение, которое будет прикреплено к запросу

    Returns:
        AIMessage: Ответ от языковой модели
    """
    file = None
    if picture:
        file = picture.file.read()
    return await run_llm_pipeline(
        str(request.dialog_id),
        request.query,
        file
    )


@chat_router.post("/v1/chat/completion/audio",
                 summary="Обработка аудиозапроса",
                 description="Загрузка аудиофайла, его преобразование в текст через ASR и обработка языковой моделью")
async def audio_answer(
    dialog_id: UUID,
    audio:  UploadFile = File(...),
    picture: UploadFile | None = None
):
    """
    Отправка аудиозапроса и необязательного изображения в чат.

    Args:
        dialog_id: Идентификатор диалога
        audio: Аудиофайл, который будет преобразован в текст с помощью ASR
        picture: Необязательное изображение, которое будет прикреплено к запросу

    Returns:
        Ответ от языковой модели

    Raises:
        Exception: Если аудиофайл не содержит имя файла или не удалось получить текст из аудио
    """
    file = None
    if not audio.filename:
        raise Exception("FILE WIHTOUT FILENAME")
    if picture:
        file = picture.file.read()
    query = await ASR().transcribe(audio.file.read())
    if not query.get("text"):
        raise Exception("NOT FOUND TEXT IN AUDIO")
    return await run_llm_pipeline(
        str(dialog_id),
        query['text'],
        file
    )

@chat_router.post("/v1/chat/clear",
                 summary="Очистка истории чата",
                 description="Удаление всей истории диалога по указанному идентификатору")
async def clear_chat(dialog_id: UUID):
    """
    Очистка истории чата по идентификатору диалога.

    Args:
        dialog_id: Идентификатор диалога, история которого должна быть очищена
    """
    await clear_chat_history(str(dialog_id))