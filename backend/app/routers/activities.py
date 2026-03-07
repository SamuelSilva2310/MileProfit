from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.activity import Activity
from app.models.user import User
from app.schemas.activity import ActivityCreate, ActivityResponse, ActivityUpdate
from app.utils.auth import get_current_user

router = APIRouter()


@router.post("/", response_model=ActivityResponse, status_code=status.HTTP_201_CREATED)
async def create_activity(
    body: ActivityCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    activity = Activity(user_id=user.id, **body.model_dump())
    db.add(activity)
    await db.flush()
    await db.refresh(activity)
    return ActivityResponse(
        id=activity.id,
        date=activity.date,
        start_km=activity.start_km,
        end_km=activity.end_km,
        total_km=activity.total_km,
        start_time=activity.start_time,
        end_time=activity.end_time,
    )


@router.get("/", response_model=list[ActivityResponse])
async def list_activities(
    start_date: date | None = Query(None),
    end_date: date | None = Query(None),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(Activity).where(Activity.user_id == user.id).order_by(Activity.date.desc())
    if start_date:
        query = query.where(Activity.date >= start_date)
    if end_date:
        query = query.where(Activity.date <= end_date)
    result = await db.execute(query)
    activities = result.scalars().all()
    return [
        ActivityResponse(
            id=a.id,
            date=a.date,
            start_km=a.start_km,
            end_km=a.end_km,
            total_km=a.total_km,
            start_time=a.start_time,
            end_time=a.end_time,
        )
        for a in activities
    ]


@router.get("/{activity_id}", response_model=ActivityResponse)
async def get_activity(
    activity_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Activity).where(Activity.id == activity_id, Activity.user_id == user.id)
    )
    activity = result.scalar_one_or_none()
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    return ActivityResponse(
        id=activity.id,
        date=activity.date,
        start_km=activity.start_km,
        end_km=activity.end_km,
        total_km=activity.total_km,
        start_time=activity.start_time,
        end_time=activity.end_time,
    )


@router.put("/{activity_id}", response_model=ActivityResponse)
async def update_activity(
    activity_id: int,
    body: ActivityUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Activity).where(Activity.id == activity_id, Activity.user_id == user.id)
    )
    activity = result.scalar_one_or_none()
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(activity, field, value)
    db.add(activity)
    await db.flush()
    await db.refresh(activity)
    return ActivityResponse(
        id=activity.id,
        date=activity.date,
        start_km=activity.start_km,
        end_km=activity.end_km,
        total_km=activity.total_km,
        start_time=activity.start_time,
        end_time=activity.end_time,
    )


@router.delete("/{activity_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_activity(
    activity_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Activity).where(Activity.id == activity_id, Activity.user_id == user.id)
    )
    activity = result.scalar_one_or_none()
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    await db.delete(activity)
