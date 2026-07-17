from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.dependencies.auth import get_current_user
from app.models.transaction import Transaction
from app.models.user import User
from app.schemas.transaction import TransactionCreate, TransactionRead, TransactionUpdate
from app.services.transaction_service import (
    create_transaction,
    get_category_for_user,
    get_transaction,
    list_transactions,
    update_transaction,
)

router = APIRouter(prefix="/transactions", tags=["transactions"])


@router.post("", response_model=TransactionRead, status_code=status.HTTP_201_CREATED)
async def create_transaction_route(
    payload: TransactionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Transaction:
    if payload.category_id is not None:
        category = await get_category_for_user(db, current_user.id, payload.category_id)
        if category is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Category not found"
            )
    return await create_transaction(db, current_user.id, payload)


@router.get("", response_model=list[TransactionRead])
async def list_transactions_route(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[Transaction]:
    return await list_transactions(db, current_user.id, limit, offset)


@router.get("/{transaction_id}", response_model=TransactionRead)
async def get_transaction_route(
    transaction_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Transaction:
    transaction = await get_transaction(db, current_user.id, transaction_id)
    if transaction is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found"
        )
    return transaction


@router.put("/{transaction_id}", response_model=TransactionRead)
async def update_transaction_route(
    transaction_id: int,
    payload: TransactionUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Transaction:
    transaction = await get_transaction(db, current_user.id, transaction_id)
    if transaction is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found"
        )

    if "category_id" in payload.model_fields_set and payload.category_id is not None:
        category = await get_category_for_user(db, current_user.id, payload.category_id)
        if category is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Category not found"
            )

    return await update_transaction(db, transaction, payload)
