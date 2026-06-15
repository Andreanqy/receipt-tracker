from calendar import monthrange
from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.crud.analytics import get_summary
from app.database import get_db
from app.models.user import User
from app.schemas.analytics import AnalyticsSummary

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/summary", response_model=AnalyticsSummary)
async def summary(
    from_date: date | None = Query(None, alias="from"),
    to_date: date | None = Query(None, alias="to"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    today = date.today()
    if from_date is None:
        from_date = today.replace(day=1)
    if to_date is None:
        to_date = today.replace(day=monthrange(today.year, today.month)[1])

    data = await get_summary(db, current_user.id, from_date, to_date)
    return AnalyticsSummary(from_date=from_date, to_date=to_date, **data)
