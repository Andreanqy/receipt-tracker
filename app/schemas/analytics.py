from datetime import date
from decimal import Decimal
from pydantic import BaseModel


class CategoryStat(BaseModel):
    category: str
    sum: Decimal


class DayStat(BaseModel):
    date: date
    sum: Decimal


class AnalyticsSummary(BaseModel):
    from_date: date
    to_date: date
    total_sum: Decimal
    total_receipts: int
    by_category: list[CategoryStat]
    by_day: list[DayStat]
