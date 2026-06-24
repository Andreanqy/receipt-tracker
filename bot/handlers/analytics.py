from datetime import date, datetime, timedelta
from io import BytesIO

import matplotlib.pyplot as plt
from aiogram import F, Router
from aiogram.filters import Command
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    BufferedInputFile,
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)
from sqlalchemy import select

from app.database import async_session_maker
from app.models.user import User
from bot.services.api import get_summary

router = Router()


class PeriodCallback(CallbackData, prefix="period"):
    value: str


class SummaryStates(StatesGroup):
    waiting_from = State()
    waiting_to = State()


def _period_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Сегодня", callback_data=PeriodCallback(value="today").pack()),
            InlineKeyboardButton(text="За неделю", callback_data=PeriodCallback(value="week").pack()),
        ],
        [
            InlineKeyboardButton(text="За месяц", callback_data=PeriodCallback(value="month").pack()),
            InlineKeyboardButton(text="За год", callback_data=PeriodCallback(value="year").pack()),
        ],
        [
            InlineKeyboardButton(text="Другой период", callback_data=PeriodCallback(value="custom").pack()),
        ],
    ])


def _parse_date(text: str) -> date:
    return datetime.strptime(text.strip(), "%d-%m-%Y").date()


async def _send_summary(message: Message, chat_id: int, from_date: date, to_date: date):
    async with async_session_maker() as db:
        result = await db.execute(select(User).where(User.telegram_chat_id == chat_id))
        user = result.scalar_one_or_none()

    if not user or not user.bot_token:
        await message.answer("Сначала зарегистрируйтесь: /start")
        return

    summary = await get_summary(user.bot_token, from_date.isoformat(), to_date.isoformat())
    if summary is None:
        await message.answer("Не удалось получить статистику. Попробуйте позже.")
        return

    from_str = from_date.strftime("%d.%m.%Y")
    to_str = to_date.strftime("%d.%m.%Y")
    await message.answer(
        f"Статистика за {from_str} — {to_str}\n\n"
        f"Итого: {summary['total_sum']} ₽ ({summary['total_receipts']} чеков)"
    )

    if summary["by_category"]:
        labels = [c["category"] for c in summary["by_category"]]
        values = [float(c["sum"]) for c in summary["by_category"]]

        fig, ax = plt.subplots(figsize=(8, 5))
        wedges, _, autotexts = ax.pie(values, autopct="%1.1f%%", startangle=90)
        ax.legend(wedges, labels, title="Категории", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))
        ax.set_title("Расходы по категориям")

        buf = BytesIO()
        fig.savefig(buf, format="png", bbox_inches="tight")
        buf.seek(0)
        plt.close(fig)

        await message.answer_photo(BufferedInputFile(buf.read(), filename="summary.png"))


@router.message(Command("summary"))
@router.message(F.text == "Получить статистику")
async def cmd_summary(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Выберите период:", reply_markup=_period_keyboard())


@router.callback_query(PeriodCallback.filter())
async def handle_period(callback: CallbackQuery, callback_data: PeriodCallback, state: FSMContext):
    today = date.today()

    if callback_data.value == "custom":
        await state.set_state(SummaryStates.waiting_from)
        await callback.message.answer("Начальная дата (ДД-ММ-ГГГГ):")
        await callback.answer()
        return

    if callback_data.value == "today":
        from_date = to_date = today
    elif callback_data.value == "week":
        from_date, to_date = today - timedelta(days=7), today
    elif callback_data.value == "month":
        from_date, to_date = today.replace(day=1), today
    else:  # year
        from_date, to_date = today.replace(month=1, day=1), today

    await callback.answer()
    await _send_summary(callback.message, callback.message.chat.id, from_date, to_date)


@router.message(SummaryStates.waiting_from)
async def handle_from(message: Message, state: FSMContext):
    try:
        from_date = _parse_date(message.text)
    except ValueError:
        await message.answer("Неверный формат. Введите ДД-ММ-ГГГГ:")
        return
    await state.update_data(from_date=from_date.isoformat())
    await state.set_state(SummaryStates.waiting_to)
    await message.answer("Конечная дата (ДД-ММ-ГГГГ):")


@router.message(SummaryStates.waiting_to)
async def handle_to(message: Message, state: FSMContext):
    try:
        to_date = _parse_date(message.text)
    except ValueError:
        await message.answer("Неверный формат. Введите ДД-ММ-ГГГГ:")
        return

    data = await state.get_data()
    await state.clear()
    from_date = date.fromisoformat(data["from_date"])
    await _send_summary(message, message.chat.id, from_date, to_date)
