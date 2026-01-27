"""Seat reservation model for handling temporary holds."""

from typing import Optional
from datetime import datetime, timedelta
from sqlmodel import SQLModel, Field, Relationship

from app.models.user import User
from app.models.cinema import Seat
from app.models.screening import Screening


class SeatReservation(SQLModel, table=True):
    """
    SeatReservation model - represents temporary seat holds before booking.
    
    This model handles the critical concurrency aspect by temporarily reserving
    seats for a user during the booking process (typically 5-10 minutes).
    """
    __tablename__ = "seat_reservation"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    screening_id: int = Field(foreign_key="screening.id")
    seat_id: int = Field(foreign_key="seat.id")
    user_id: int = Field(foreign_key="user.id")
    reserved_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime = Field(default_factory=lambda: datetime.utcnow() + timedelta(minutes=5))
    status: str = Field(default="active", max_length=20)  # active, expired, booked, cancelled
    
    # Relationships
    screening: Optional[Screening] = Relationship()
    seat: Optional[Seat] = Relationship()
    user: Optional[User] = Relationship()
    
    class Config:
        # Ensure one seat can only be reserved once per screening at a time
        indexes = [
            # Partial unique constraint for active/booked reservations 
            {"fields": ["screening_id", "seat_id", "status"], "unique": True, "postgresql_where": "status IN ('active', 'booked')"},
            {"fields": ["expires_at", "status"]},
            {"fields": ["user_id", "status"]},
        ]