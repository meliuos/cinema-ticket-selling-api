"""Pydantic schemas for Ticket-related API operations."""

from datetime import datetime
from typing import List
from sqlmodel import SQLModel, Field


class TicketBase(SQLModel):
    """Base model for Ticket with shared fields."""
    screening_id: int
    seat_id: int
    price: float = Field(gt=0)
    status: str = Field(default="booked", max_length=50)


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
