"""Seat routes."""

from fastapi import APIRouter, Depends, status
from sqlmodel import Session, select
from typing import List

from app.config import settings
from app.database import get_session
from app.models.cinema import Seat
from app.models.user import User
from app.schemas.cinema import SeatRead, SeatBulkCreate
from app.services.cinema import bulk_create_seats
from app.services.auth import get_current_admin_user

router = APIRouter(prefix=settings.API_V1_PREFIX, tags=["Seats"])


@router.post(
    "/rooms/{room_id}/seats/bulk",
    response_model=List[SeatRead],
    status_code=status.HTTP_201_CREATED
)
def create_seats_bulk(
    room_id: int,
    data: SeatBulkCreate,
    session: Session = Depends(get_session),
    current_admin: User = Depends(get_current_admin_user)
):
    """Bulk create seats for a room (always 7 rows x 10 seats) (admin only)."""
    seats = bulk_create_seats(session, room_id, data)
    return seats


@router.get("/rooms/{room_id}/seats/", response_model=List[SeatRead])
def list_room_seats(room_id: int, session: Session = Depends(get_session)):
    """List all seats in a room."""
    seats = session.exec(select(Seat).where(Seat.room_id == room_id)).all()
    return seats
