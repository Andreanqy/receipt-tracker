import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.receipt import Receipt, ReceiptStatus
from app.models.receipt_item import ReceiptItem


async def get_receipt_by_id(db: AsyncSession, receipt_id: uuid.UUID) -> Receipt | None:
    result = await db.execute(select(Receipt).where(Receipt.id == receipt_id))
    return result.scalar_one_or_none()


async def get_receipt_by_id_and_user(
    db: AsyncSession, receipt_id: uuid.UUID, user_id: uuid.UUID
) -> Receipt | None:
    result = await db.execute(
        select(Receipt).where(Receipt.id == receipt_id, Receipt.user_id == user_id)
    )
    return result.scalar_one_or_none()


async def update_receipt_after_processing(
    db: AsyncSession,
    receipt: Receipt,
    *,
    status: ReceiptStatus,
    total_sum: Decimal | None = None,
    qr_raw_data: str | None = None,
    operation_time: datetime | None = None,
) -> None:
    receipt.status = status
    if total_sum is not None:
        receipt.total_sum = total_sum
    if qr_raw_data is not None:
        receipt.qr_raw_data = qr_raw_data
    if operation_time is not None:
        receipt.operation_time = operation_time
    await db.commit()


async def create_receipt_items(
    db: AsyncSession,
    receipt_id: uuid.UUID,
    items: list[dict],
) -> None:
    for item in items:
        db.add(ReceiptItem(
            receipt_id=receipt_id,
            name=item["name"],
            price=item["price"],
            quantity=item.get("quantity", Decimal("1.000")),
            sum=item["sum"],
            category=item.get("category"),
        ))
    await db.commit()


async def create_receipt(
    db: AsyncSession,
    *,
    receipt_id: uuid.UUID,
    user_id: uuid.UUID,
    filepath: str,
) -> Receipt:
    receipt = Receipt(
        id=receipt_id,
        user_id=user_id,
        total_sum=Decimal("0"),
        filepath=filepath,
        status=ReceiptStatus.PROCESSING,
    )
    db.add(receipt)
    await db.commit()
    await db.refresh(receipt)
    return receipt
