"""Schemas for seat reservation operations."""

from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel
from app.schemas.cinema import SeatRead
from app.schemas.user import UserRead


class SeatReservationBase(BaseModel):
    """Base schema for seat reservations."""
    screening_id: int
    seat_id: int


class SeatReservationCreate(BaseModel):
    """Schema for creating seat reservations."""
    screening_id: int
    seat_ids: Optional[List[int]] = None  
    seat_id: Optional[int] = None  
    
    def get_seat_ids(self) -> List[int]:
        """Get seat IDs from either seat_ids list or single seat_id."""
        if self.seat_ids is not None:
            return self.seat_ids
        elif self.seat_id is not None:
            return [self.seat_id]
        else:
            raise ValueError("Either seat_ids or seat_id must be provided")


class SeatReservationRead(SeatReservationBase):
    """Schema for reading seat reservations."""
    id: int
    user_id: int
    reserved_at: datetime
    expires_at: datetime
    status: str
    seat: Optional[SeatRead] = None
    user: Optional[UserRead] = None
    
    class Config:
        from_attributes = True


class SeatReservationResponse(BaseModel):
    """Schema for seat reservation response."""
    reservations: List[SeatReservationRead]
    expires_in_minutes: int
    message: str


class SeatAvailabilityRead(BaseModel):
    """Schema for seat availability response."""
    seat: SeatRead
    status: str  # available, reserved, booked, reserved_by_me
    reserved_by: Optional[int] = None  # user_id if reserved
    is_mine: bool = False  # True if the current user has this reservation
    expires_at: Optional[datetime] = None  # if reserved
    
    class Config:
        from_attributes = True