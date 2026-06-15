import uuid
from datetime import date, datetime, timezone

from sqlalchemy import cast, func, select, Date
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.receipt import Receipt, ReceiptStatus
from app.models.receipt_item import ReceiptItem


async def get_summary(
    db: AsyncSession,
    user_id: uuid.UUID,
    from_date: date,
    to_date: date,
) -> dict:
    from_dt = datetime(from_date.year, from_date.month, from_date.day)
    to_dt = datetime(to_date.year, to_date.month, to_date.day, 23, 59, 59)

    filters = [
        Receipt.user_id == user_id,
        Receipt.status == ReceiptStatus.COMPLETED,
        Receipt.created_at >= from_dt,
        Receipt.created_at <= to_dt,
    ]

    totals = (await db.execute(
        select(
            func.coalesce(func.sum(Receipt.total_sum), 0).label("total_sum"),
            func.count(Receipt.id).label("total_receipts"),
        ).where(*filters)
    )).one()

    by_category = (await db.execute(
        select(
            ReceiptItem.category,
            func.sum(ReceiptItem.sum).label("sum"),
        )
        .join(Receipt, ReceiptItem.receipt_id == Receipt.id)
        .where(*filters)
        .group_by(ReceiptItem.category)
        .order_by(func.sum(ReceiptItem.sum).desc())
    )).all()

    by_day = (await db.execute(
        select(
            cast(Receipt.created_at, Date).label("day"),
            func.sum(Receipt.total_sum).label("sum"),
        )
        .where(*filters)
        .group_by("day")
        .order_by("day")
    )).all()

    return {
        "total_sum": totals.total_sum,
        "total_receipts": totals.total_receipts,
        "by_category": [{"category": r.category or "Прочее", "sum": r.sum} for r in by_category],
        "by_day": [{"date": r.day, "sum": r.sum} for r in by_day],
    }
