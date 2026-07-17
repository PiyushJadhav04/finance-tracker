from datetime import date as date_, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, model_validator


class TransactionCreate(BaseModel):
    amount: Decimal
    category_id: int | None = None
    description: str | None = None
    date: date_


class TransactionUpdate(BaseModel):
    amount: Decimal | None = None
    category_id: int | None = None
    description: str | None = None
    date: date_ | None = None

    @model_validator(mode="after")
    def reject_explicit_null_on_required_fields(self) -> "TransactionUpdate":
        # amount/date are NOT NULL columns. A field left out of the request
        # body is fine (we skip it via exclude_unset), but a field the
        # client explicitly sent as `null` would otherwise reach the DB and
        # fail as an ugly 500 instead of a clean validation error.
        for field in ("amount", "date"):
            if field in self.model_fields_set and getattr(self, field) is None:
                raise ValueError(f"{field} cannot be null")
        return self


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
