from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field


class Ticket(SQLModel, table=True):
    """Ticket model - represents booked tickets."""
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    screening_id: int = Field(foreign_key="screening.id")
    seat_id: int = Field(foreign_key="seat.id")
    price: float = Field(gt=0)
    status: str = Field(default="pending", max_length=50)  # pending, confirmed, cancelled
    booked_at: datetime = Field(default_factory=datetime.utcnow)
    confirmed_at: Optional[datetime] = None
    payment_id: Optional[str] = Field(default=None, max_length=255)  # For idempotency
    
    class Config:
        indexes = [
            {"fields": ["screening_id", "seat_id"], "unique": True},
            {"fields": ["payment_id"], "unique": True}  
        ]
