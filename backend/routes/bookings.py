from fastapi import APIRouter, Depends, Form, Query
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, validator
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import and_
from typing import Optional

from .. import models, auth
from ..database import get_db

router = APIRouter()

class BookingCreate(BaseModel):
    check_in: datetime
    check_out: datetime
    adults: int
    children: int
    rooms: list[str]


class BookingOut(BaseModel):
    id: int
    check_in: datetime
    check_out: datetime
    adults: int
    children: int
    rooms: list[str]

    class Config:
        from_attributes = True

    @validator("rooms", pre=True)
    def split_rooms(cls, v):
        if isinstance(v, str):
            return v.split(",")
        return v


@router.post("/bookings")
async def create_booking(
    check_in: str = Form(...),
    check_out: str = Form(...),
    adults: int = Form(...),
    kids: int = Form(0),
    rooms: list[str] = Form(...),
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    check_in_date = datetime.strptime(check_in, "%Y-%m-%d")
    check_out_date = datetime.strptime(check_out, "%Y-%m-%d")

    new_booking = models.Booking(
        user_id=current_user.id,
        check_in=check_in_date,
        check_out=check_out_date,
        adults=adults,
        children=kids,
        rooms=",".join(rooms),
    )
    db.add(new_booking)
    await db.commit()
    await db.refresh(new_booking)

    return RedirectResponse(url="/resibo", status_code=303)


@router.get("/bookings/me", response_model=list[BookingOut])
async def get_my_bookings(
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    result = await db.execute(
        select(models.Booking).where(models.Booking.user_id == current_user.id)
    )
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

@router.get("/availability")
async def check_availability(
    check_in: str,
    check_out: str,
    rooms: Optional[list[str]] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    check_in_date = datetime.strptime(check_in, "%Y-%m-%d")
    check_out_date = datetime.strptime(check_out, "%Y-%m-%d")

    result = await db.execute(
        select(models.Booking).where(
            and_(
                models.Booking.check_in < check_out_date,
                models.Booking.check_out > check_in_date,
            )
        )
    )
    existing_bookings = result.scalars().all()

    reserved_rooms = set()
    for booking in existing_bookings:
        reserved_rooms.update(booking.rooms.split(","))

    all_rooms = ["Macau", "Morocco", "Paris", "Portugal", "Spain", "Vietnam"]

    target_rooms = rooms if rooms else all_rooms
    available = [room for room in target_rooms if room not in reserved_rooms]

    return {
        "requested": target_rooms,
        "available": available,
        "unavailable": [room for room in target_rooms if room in reserved_rooms],
    }