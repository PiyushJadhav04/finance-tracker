from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.category import Category
from app.models.transaction import Transaction
from app.schemas.transaction import TransactionCreate


async def get_category_for_user(db: AsyncSession, user_id: int, category_id: int) -> Category | None:
    # a category is usable by this user if it's global (user_id IS NULL)
    # or owned by them — never let a client attach someone else's category
    result = await db.execute(
        select(Category).where(
            Category.id == category_id,
            (Category.user_id == user_id) | (Category.user_id.is_(None)),
        )
    )
    return result.scalar_one_or_none()


async def create_transaction(
    db: AsyncSession, user_id: int, data: TransactionCreate
) -> Transaction:
    transaction = Transaction(
        user_id=user_id,
        category_id=data.category_id,
        amount=data.amount,
        description=data.description,
        date=data.date,
    )
    db.add(transaction)
    await db.commit()
    await db.refresh(transaction)
    return transaction
