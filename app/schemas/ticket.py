"""Pydantic schemas for Ticket-related API operations."""

from datetime import datetime
from typing import List, Optional
from sqlmodel import SQLModel, Field


class TicketBase(SQLModel):
    """Base model for Ticket with shared fields."""
    screening_id: int
    seat_id: int
    price: float = Field(gt=0)
    status: str = Field(default="pending", max_length=50)


class TicketCreate(SQLModel):
    """Schema for creating a ticket (booking)."""
    screening_id: int
    seat_ids: List[int]  # Can book multiple seats at once


class TicketRead(SQLModel):
    """Schema for reading a ticket."""
    id: int
    user_id: int
    screening_id: int
    seat_id: int
    price: float
    status: str
    booked_at: datetime
    confirmed_at: Optional[datetime] = None


class TicketStatusUpdate(SQLModel):
    """Schema for updating ticket status."""
    status: str = Field(description="New status: pending, confirmed, or cancelled")


class TicketConfirmPayment(SQLModel):
    """Schema for confirming payment."""
    payment_method: str = Field(description="Payment method used")
    transaction_id: Optional[str] = Field(None, description="External transaction ID")


class BookFromReservationRequest(SQLModel):
    """Book tickets from active seat reservations (after payment)."""
    reservation_ids: List[int]
    payment_id: str


class BookFromReservationResponse(SQLModel):
    """Response containing created tickets."""
    tickets: List[TicketRead]
