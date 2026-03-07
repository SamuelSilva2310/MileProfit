from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.earning import Earning
from app.models.user import User
from app.schemas.earning import EarningCreate, EarningResponse, EarningUpdate
from app.utils.auth import get_current_user

router = APIRouter()


@router.post("/", response_model=EarningResponse, status_code=status.HTTP_201_CREATED)
async def create_earning(
    body: EarningCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    earning = Earning(user_id=user.id, **body.model_dump())
    db.add(earning)
    await db.flush()
    await db.refresh(earning)
    return earning


@router.get("/", response_model=list[EarningResponse])
async def list_earnings(
    start_date: date | None = Query(None),
    end_date: date | None = Query(None),
    platform: str | None = Query(None),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(Earning).where(Earning.user_id == user.id).order_by(Earning.date.desc())
    if start_date:
        query = query.where(Earning.date >= start_date)
    if end_date:
        query = query.where(Earning.date <= end_date)
    if platform:
        query = query.where(Earning.platform == platform)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{earning_id}", response_model=EarningResponse)
async def get_earning(
    earning_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Earning).where(Earning.id == earning_id, Earning.user_id == user.id)
    )
    earning = result.scalar_one_or_none()
    if not earning:
        raise HTTPException(status_code=404, detail="Earning not found")
    return earning


@router.put("/{earning_id}", response_model=EarningResponse)
async def update_earning(
    earning_id: int,
    body: EarningUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Earning).where(Earning.id == earning_id, Earning.user_id == user.id)
    )
    earning = result.scalar_one_or_none()
    if not earning:
        raise HTTPException(status_code=404, detail="Earning not found")
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(earning, field, value)
    db.add(earning)
    await db.flush()
    await db.refresh(earning)
    return earning


@router.delete("/{earning_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_earning(
    earning_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Earning).where(Earning.id == earning_id, Earning.user_id == user.id)
    )
    earning = result.scalar_one_or_none()
    if not earning:
        raise HTTPException(status_code=404, detail="Earning not found")
    await db.delete(earning)
