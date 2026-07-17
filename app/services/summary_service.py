from calendar import monthrange
from datetime import date
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.category import Category
from app.models.transaction import Transaction
from app.schemas.summary import CategorySpend


def _month_bounds(year: int, month: int) -> tuple[date, date]:
    start = date(year, month, 1)
    end = date(year, month, monthrange(year, month)[1])
    return start, end


async def get_total_spend(db: AsyncSession, user_id: int, year: int, month: int) -> Decimal:
    start, end = _month_bounds(year, month)
    result = await db.execute(
        select(func.coalesce(func.sum(Transaction.amount), 0)).where(
            Transaction.user_id == user_id,
            Transaction.date >= start,
            Transaction.date <= end,
        )
    )
    return result.scalar_one()


async def get_spend_by_category(
    db: AsyncSession, user_id: int, year: int, month: int
) -> list[CategorySpend]:
    start, end = _month_bounds(year, month)
    result = await db.execute(
        select(
            Transaction.category_id,
            Category.name,
            func.sum(Transaction.amount).label("total"),
        )
        .outerjoin(Category, Transaction.category_id == Category.id)
        .where(
            Transaction.user_id == user_id,
            Transaction.date >= start,
            Transaction.date <= end,
        )
        .group_by(Transaction.category_id, Category.name)
        .order_by(func.sum(Transaction.amount).desc())
    )
    return [
        CategorySpend(
            category_id=category_id,
            category_name=name if category_id is not None else "Uncategorized",
            total=total,
        )
        for category_id, name, total in result.all()
    ]
