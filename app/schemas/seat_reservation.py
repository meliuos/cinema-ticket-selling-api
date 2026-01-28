from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class SeatRef(BaseModel):
    id: int
    row_label: str
    seat_number: int
    seat_type: str


class SeatAvailabilityRead(BaseModel):
    """
    Mirrors the Angular backend payload so both Angular + Flutter can share.
    """

    seat_id: int
    status: str  # available | reserved | reserved_by_me | booked
    reserved_by: Optional[int] = None
    is_mine: bool = False
    expires_at: Optional[datetime] = None
    seat: Optional[SeatRef] = None


class SeatReservationCreate(BaseModel):
    screening_id: int
    seat_id: Optional[int] = None
    seat_ids: Optional[List[int]] = None

    def get_seat_ids(self) -> List[int]:
        if self.seat_ids is not None:
            if not isinstance(self.seat_ids, list) or len(self.seat_ids) == 0:
                raise ValueError("seat_ids must be a non-empty list")
            return [int(x) for x in self.seat_ids]
        if self.seat_id is not None:
            return [int(self.seat_id)]
        raise ValueError("Provide seat_id or seat_ids")


class SeatReservationRead(BaseModel):
    id: int
    user_id: int
    screening_id: int
    seat_id: int
    status: str
    created_at: datetime
    expires_at: datetime


class SeatReservationResponse(BaseModel):
    reservations: List[SeatReservationRead] = Field(default_factory=list)
    expires_in_minutes: int
    message: str
