import asyncio
import uuid
from decimal import Decimal
from datetime import datetime, timezone
from io import BytesIO

import httpx
from aiogram import Bot
from PIL import Image
from pyzbar.pyzbar import decode

from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool

from app.config import settings
from app.models.user import User
from app.services.categorization import categorize_items
from app.crud.receipt import (
    create_receipt_items,
    get_receipt_by_id,
    update_receipt_after_processing,
)
from app.models.receipt import ReceiptStatus
from app.services.s3 import s3_service
from app.tasks.celery_app import celery_app

# NullPool: connections are never reused between tasks, avoiding event loop conflicts
_task_engine = create_async_engine(settings.DATABASE_URL, poolclass=NullPool)
_task_session_maker = async_sessionmaker(_task_engine, autocommit=False, autoflush=False, expire_on_commit=False)


@celery_app.task(bind=True, max_retries=3, default_retry_delay=10)
def process_receipt(self, receipt_id: str) -> None:
    is_last_attempt = self.request.retries >= self.max_retries
    retry_exc, fail_exc = asyncio.run(_handle(receipt_id, is_last_attempt))

    if retry_exc is not None:
        raise self.retry(exc=retry_exc)
    if fail_exc is not None:
        raise fail_exc


async def _handle(
    receipt_id: str, is_last_attempt: bool
) -> tuple[Exception | None, Exception | None]:
    try:
        await _process(receipt_id)
        return None, None
    except httpx.HTTPError as exc:
        if is_last_attempt:
            await _mark_failed(receipt_id)
            return None, exc
        return exc, None
    except Exception as exc:
        await _mark_failed(receipt_id)
        return None, exc


async def _mark_failed(receipt_id: str) -> None:
    async with _task_session_maker() as db:
        receipt = await get_receipt_by_id(db, uuid.UUID(receipt_id))
        if not receipt:
            return
        await update_receipt_after_processing(db, receipt, status=ReceiptStatus.FAILED)

        user_result = await db.execute(select(User).where(User.id == receipt.user_id))
        user = user_result.scalar_one_or_none()
        if user and user.telegram_chat_id:
            bot = Bot(token=settings.TELEGRAM_BOT_SECRET_KEY)
            try:
                await bot.send_message(user.telegram_chat_id, "Не удалось обработать чек. Убедитесь, что на фото виден QR-код.")
            finally:
                await bot.session.close()


async def _process(receipt_id: str) -> None:
    async with _task_session_maker() as db:
        receipt = await get_receipt_by_id(db, uuid.UUID(receipt_id))
        if receipt is None:
            return

        object_name = receipt.filepath[len(settings.MINIO_BUCKET_NAME) + 1:]
        file_bytes = await s3_service.download_file(object_name)

        qr_raw = None
        async with httpx.AsyncClient(timeout=30.0) as client:
            if settings.USE_QR_FILE:
                response = await client.post(
                    "https://proverkacheka.com/api/v1/check/get",
                    data={"token": settings.PROVERKACHEKA_TOKEN},
                    files={"qrfile": ("receipt.jpg", file_bytes, "image/jpeg")},
                )
            else:
                image = Image.open(BytesIO(file_bytes))
                codes = decode(image)
                if not codes:
                    raise ValueError("No QR code found in image")
                qr_raw = codes[0].data.decode("utf-8")
                response = await client.post(
                    "https://proverkacheka.com/api/v1/check/get",
                    json={"token": settings.PROVERKACHEKA_TOKEN, "qrraw": qr_raw},
                )
            response.raise_for_status()
            data = response.json()

        if data.get("code") != 1:
            raise ValueError(f"proverkacheka API error: code={data.get('code')}")

        receipt_json = data["data"]["json"]
        total_sum = Decimal(str(receipt_json["totalSum"])) / 100
        operation_time = datetime.fromisoformat(str(receipt_json["dateTime"]))
        raw_items = receipt_json.get("items", [])
        items = [
            {
                "name": item["name"],
                "price": Decimal(str(item["price"])) / 100,
                "quantity": Decimal(str(item.get("quantity", 1))),
                "sum": Decimal(str(item["sum"])) / 100,
            }
            for item in raw_items
        ]

        categories = await categorize_items([i["name"] for i in items])
        for item, category in zip(items, categories):
            item["category"] = category

        await create_receipt_items(db, receipt.id, items)
        await update_receipt_after_processing(
            db,
            receipt,
            status=ReceiptStatus.COMPLETED,
            total_sum=total_sum,
            qr_raw_data=qr_raw,
            operation_time=operation_time,
        )

        user_result = await db.execute(select(User).where(User.id == receipt.user_id))
        user = user_result.scalar_one_or_none()
        if user and user.telegram_chat_id:
            item_lines = "\n".join(f"  • {i['name']}: {i['sum']} ₽" for i in items)
            text = f"Чек обработан!\n\nПозиции:\n{item_lines}\n\nИтого: {total_sum} ₽"
            bot = Bot(token=settings.TELEGRAM_BOT_SECRET_KEY)
            try:
                await bot.send_message(user.telegram_chat_id, text)
            finally:
                await bot.session.close()
