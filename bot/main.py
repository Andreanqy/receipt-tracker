import asyncio
import logging
from aiogram import Bot, Dispatcher
from app.config import settings
from bot.handlers import start, receipt, analytics

logging.basicConfig(level=logging.INFO)

async def main():
    bot = Bot(token=settings.TELEGRAM_BOT_SECRET_KEY)
    dp = Dispatcher()
    dp.include_router(start.router)
    dp.include_router(receipt.router)
    dp.include_router(analytics.router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
