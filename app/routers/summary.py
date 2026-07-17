from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.summary import SummaryResponse
from app.services.summary_service import get_spend_by_category, get_total_spend

router = APIRouter(tags=["summary"])


@router.get("/summary", response_model=SummaryResponse)
async def get_summary_route(
    year: int | None = Query(None),
    month: int | None = Query(None, ge=1, le=12),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SummaryResponse:
    today = date.today()
    target_year = year or today.year
    target_month = month or today.month

    total_spend = await get_total_spend(db, current_user.id, target_year, target_month)
    by_category = await get_spend_by_category(db, current_user.id, target_year, target_month)

    return SummaryResponse(
        year=target_year,
        month=target_month,
        total_spend=total_spend,
        by_category=by_category,
    )
