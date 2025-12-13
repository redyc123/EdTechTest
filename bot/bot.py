import asyncio
import uuid
import os
from typing import Dict

from aiogram import Bot, Dispatcher, F
from aiogram.types import (
    Message,
)
from aiogram.filters import Command
from dotenv import load_dotenv

from llm_client import LLMServiceClient

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
BASE_URL = os.getenv("BASE_URL")
SECRET_TOKEN = os.getenv("SECRET_TOKEN")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# dialog_id для каждого пользователя
user_dialogs: Dict[int, uuid.UUID] = {}

# LLM client
llm_client = LLMServiceClient(BASE_URL)


# -------------------- utils --------------------

async def get_dialog_id(user_id: int) -> uuid.UUID:
    if user_id not in user_dialogs:
        user_dialogs[user_id] = uuid.uuid4()
    return user_dialogs[user_id]


async def ensure_access_token():
    if llm_client.access_token:
        return

    token_response = await llm_client.generate_token(SECRET_TOKEN)
    llm_client.set_access_token(token_response["access_token"])


async def download_file(message: Message) -> bytes:
    file = await bot.get_file(message.document.file_id)
    return await bot.download_file(file.file_path)


async def download_photo(message: Message) -> bytes:
    photo = message.photo[-1]
    file = await bot.get_file(photo.file_id)
    return await bot.download_file(file.file_path)


async def download_voice(message: Message) -> bytes:
    file = await bot.get_file(message.voice.file_id)
    return await bot.download_file(file.file_path)


# -------------------- commands --------------------

@dp.message(Command("start"))
async def start(message: Message):
    await message.answer(
        "🤖 Привет! Я AI-бот.\n\n"
        "• Напиши текст\n"
        "• Отправь голосовое\n"
        "• Загрузите документ\n\n"
        "/clear — очистить историю"
    )


@dp.message(Command("clear"))
async def clear_chat(message: Message):
    await ensure_access_token()
    dialog_id = await get_dialog_id(message.from_user.id)

    await llm_client.clear_chat(dialog_id)
    await message.answer("🧹 История чата очищена")


@dp.message(Command("delete"))
async def delete_docs(message: Message):
    await ensure_access_token()
    dialog_id = await get_dialog_id(message.from_user.id)

    ids = message.text.split()[1:]
    if not ids:
        await message.answer("❌ Укажи ID документов")
        return

    await llm_client.remove_documents(dialog_id, ids)
    await message.answer("🗑 Документы удалены")


# -------------------- text --------------------

@dp.message(F.text)
async def handle_text(message: Message):
    await ensure_access_token()
    dialog_id = await get_dialog_id(message.from_user.id)

    picture = None
    if message.reply_to_message and message.reply_to_message.photo:
        picture = await download_photo(message.reply_to_message)

    response = await llm_client.text_completion(
        dialog_id=dialog_id,
        query=message.text,
        picture=picture,
    )

    await message.answer(response.get("content", "🤷 Нет ответа"))


# -------------------- voice --------------------

@dp.message(F.voice)
async def handle_voice(message: Message):
    await ensure_access_token()
    dialog_id = await get_dialog_id(message.from_user.id)

    audio_data = await download_voice(message)

    picture = None
    if message.caption and message.photo:
        picture = await download_photo(message)

    response = await llm_client.audio_completion(
        dialog_id=dialog_id,
        audio_data=audio_data,
        picture=picture,
    )

    await message.answer(response.get("content", "🎤 Нет ответа"))


# -------------------- document --------------------

@dp.message(F.document)
async def handle_document(message: Message):
    await ensure_access_token()
    dialog_id = await get_dialog_id(message.from_user.id)

    file_data = await download_file(message)
    filename = message.document.file_name

    response = await llm_client.parse_document(
        dialog_id=dialog_id,
        file_data=file_data,
        filename=filename,
    )

    ids = response.get("ids", [])
    await message.answer(
        f"📄 Документ обработан\nIDs:\n" + "\n".join(ids)
    )


# -------------------- run --------------------

async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
