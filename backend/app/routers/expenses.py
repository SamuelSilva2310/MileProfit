from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.expense import Expense
from app.models.user import User
from app.schemas.expense import ExpenseCreate, ExpenseResponse, ExpenseUpdate
from app.utils.auth import get_current_user

router = APIRouter()


@router.post("/", response_model=ExpenseResponse, status_code=status.HTTP_201_CREATED)
async def create_expense(
    body: ExpenseCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    expense = Expense(user_id=user.id, **body.model_dump())
    db.add(expense)
    await db.flush()
    await db.refresh(expense)
    return expense


@router.get("/", response_model=list[ExpenseResponse])
async def list_expenses(
    start_date: date | None = Query(None),
    end_date: date | None = Query(None),
    category: str | None = Query(None),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(Expense).where(Expense.user_id == user.id).order_by(Expense.date.desc())
    if start_date:
        query = query.where(Expense.date >= start_date)
    if end_date:
        query = query.where(Expense.date <= end_date)
    if category:
        query = query.where(Expense.category == category)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{expense_id}", response_model=ExpenseResponse)
async def get_expense(
    expense_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Expense).where(Expense.id == expense_id, Expense.user_id == user.id)
    )
    expense = result.scalar_one_or_none()
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    return expense


@router.put("/{expense_id}", response_model=ExpenseResponse)
async def update_expense(
    expense_id: int,
    body: ExpenseUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Expense).where(Expense.id == expense_id, Expense.user_id == user.id)
    )
    expense = result.scalar_one_or_none()
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(expense, field, value)
    db.add(expense)
    await db.flush()
    await db.refresh(expense)
    return expense


@router.delete("/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_expense(
    expense_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Expense).where(Expense.id == expense_id, Expense.user_id == user.id)
    )
    expense = result.scalar_one_or_none()
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    await db.delete(expense)
