from fastapi import APIRouter, Depends
from pydantic import BaseModel
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from .. import models, auth
from ..database import get_db

router = APIRouter()

class BookingCreate(BaseModel):
    check_in: datetime
    check_out: datetime
    adults: int
    children: int
    rooms: int

class BookingOut(BaseModel):
    id: int
    check_in: datetime
    check_out: datetime
    adults: int
    children: int
    rooms: int

    class Config:
        orm_mode = True


@router.post("/bookings", response_model=BookingOut)
async def create_booking(
    booking: BookingCreate,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    new_booking = models.Booking(
        user_id=current_user.id,
        **booking.dict()
    )
    db.add(new_booking)
    await db.commit()
    await db.refresh(new_booking)
    return new_booking


@router.get("/bookings/me", response_model=list[BookingOut])
async def get_my_bookings(
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    result = await db.execute(select(models.Booking).where(models.Booking.user_id == current_user.id))
    return result.scalars().all()


@router.delete("/bookings/{booking_id}")
async def delete_booking(
    booking_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    result = await db.execute(
        select(models.Booking).where(
            models.Booking.id == booking_id,
            models.Booking.user_id == current_user.id
        )
    )
    booking = result.scalars().first()
    if not booking:
        return {"msg": "Booking not found"}
    await db.delete(booking)
    await db.commit()
    return {"msg": "Booking deleted"}
