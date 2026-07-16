from datetime import date as date_, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class TransactionCreate(BaseModel):
    amount: Decimal
    category_id: int | None = None
    description: str | None = None
    date: date_


class TransactionRead(BaseModel):
    id: int
    user_id: int
    category_id: int | None
    amount: Decimal
    description: str | None
    date: date_
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
