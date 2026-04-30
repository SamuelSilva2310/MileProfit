from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.models.vehicle import Vehicle
from app.schemas.vehicle import VehicleCreate, VehicleResponse, VehicleUpdate
from app.utils.auth import get_current_user

router = APIRouter()


async def _clear_primary(user_id: int, db: AsyncSession) -> None:
    await db.execute(
        update(Vehicle).where(Vehicle.user_id == user_id).values(is_primary=False)
    )


@router.get("/", response_model=list[VehicleResponse])
async def list_vehicles(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Vehicle).where(Vehicle.user_id == user.id).order_by(Vehicle.created_at)
    )
    return result.scalars().all()


@router.post("/", response_model=VehicleResponse, status_code=status.HTTP_201_CREATED)
async def create_vehicle(
    body: VehicleCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if body.is_primary:
        await _clear_primary(user.id, db)
    vehicle = Vehicle(user_id=user.id, name=body.name.strip(), is_primary=body.is_primary)
    db.add(vehicle)
    await db.flush()
    await db.refresh(vehicle)
    return vehicle


@router.patch("/{vehicle_id}", response_model=VehicleResponse)
async def update_vehicle(
    vehicle_id: int,
    body: VehicleUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Vehicle).where(Vehicle.id == vehicle_id, Vehicle.user_id == user.id)
    )
    vehicle = result.scalar_one_or_none()
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    if body.is_primary:
        await _clear_primary(user.id, db)
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(vehicle, field, value)
    db.add(vehicle)
    await db.flush()
    await db.refresh(vehicle)
    return vehicle


@router.delete("/{vehicle_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_vehicle(
    vehicle_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Vehicle).where(Vehicle.id == vehicle_id, Vehicle.user_id == user.id)
    )
    vehicle = result.scalar_one_or_none()
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    await db.delete(vehicle)
