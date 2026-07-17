from decimal import Decimal

from pydantic import BaseModel


class CategorySpend(BaseModel):
    category_id: int | None
    category_name: str
    total: Decimal


class SummaryResponse(BaseModel):
    year: int
    month: int
    total_spend: Decimal
    by_category: list[CategorySpend]
