import uuid
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.receipt import Receipt, ReceiptStatus


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
