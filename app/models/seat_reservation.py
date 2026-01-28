from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field


class SeatReservation(SQLModel, table=True):
    """
    Temporary seat hold (reservation) for concurrency control.

    - status="active": held until expires_at
    - status="cancelled": released by user
    - status="expired": released by cleanup
    """

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    screening_id: int = Field(foreign_key="screening.id", index=True)
    seat_id: int = Field(foreign_key="seat.id", index=True)

    status: str = Field(default="active", max_length=50, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    expires_at: datetime = Field(index=True)
