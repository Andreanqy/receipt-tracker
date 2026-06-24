import uuid
from datetime import timedelta

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import KeyboardButton, Message, ReplyKeyboardMarkup
from sqlalchemy import select

from app.core.security import create_access_token
from app.database import async_session_maker
from app.models.user import User

router = Router()

_MAIN_KEYBOARD = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="Получить статистику")]],
    resize_keyboard=True,
)


@router.message(Command("start"))
async def cmd_start(message: Message):
    chat_id = message.chat.id

    async with async_session_maker() as db:
        result = await db.execute(select(User).where(User.telegram_chat_id == chat_id))
        user = result.scalar_one_or_none()

        if not user:
            user_id = uuid.uuid4()
            bot_token = create_access_token(
                data={"sub": str(user_id)},
                expires_delta=timedelta(days=36500),
            )
            db.add(User(
                id=user_id,
                email=f"tg_{chat_id}@telegram.local",
                hashed_password="",
                telegram_chat_id=chat_id,
                bot_token=bot_token,
            ))
            await db.commit()
            await message.answer(
                "Добро пожаловать! Аккаунт создан.\n\n"
                "Отправьте фото чека с QR-кодом — я добавлю его в базу данных.",
                reply_markup=_MAIN_KEYBOARD,
            )
        else:
            await message.answer(
                "Вы уже зарегистрированы.\n\n"
                "Отправьте фото чека или нажмите кнопку для статистики.",
                reply_markup=_MAIN_KEYBOARD,
            )
