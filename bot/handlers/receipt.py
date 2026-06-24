from aiogram import Bot, F, Router
from aiogram.types import Message
from sqlalchemy import select

from app.database import async_session_maker
from app.models.user import User
from bot.services.api import upload_receipt

router = Router()


@router.message(F.photo)
async def handle_photo(message: Message, bot: Bot):
    chat_id = message.chat.id

    async with async_session_maker() as db:
        result = await db.execute(select(User).where(User.telegram_chat_id == chat_id))
        user = result.scalar_one_or_none()

    if not user or not user.bot_token:
        await message.answer("Сначала зарегистрируйтесь: /start")
        return

    photo = message.photo[-1]
    file = await bot.get_file(photo.file_id)
    file_bytes = await bot.download_file(file.file_path)

    await message.answer("Ваш чек получен и принят в обработку.")
    await upload_receipt(user.bot_token, file_bytes.read(), f"{photo.file_id}.jpg")
