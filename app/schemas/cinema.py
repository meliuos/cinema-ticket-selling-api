"""Pydantic schemas for Cinema-related API operations."""

from datetime import datetime
from typing import Optional, List
from sqlmodel import SQLModel, Field

class CinemaBase(SQLModel):
    """Base model for Cinema with shared fields."""
    name: str = Field(max_length=255)
    address: str = Field(max_length=500)
    city: str = Field(max_length=100)
    amenities: Optional[List[str]] = None

class CinemaCreate(CinemaBase):
    """Schema for creating a cinema."""
    pass

class CinemaRead(CinemaBase):
    """Schema for reading a cinema."""
    id: int
    created_at: datetime

class RoomBase(SQLModel):
    """Base model for Room with shared fields."""
    name: str = Field(max_length=100)

class RoomCreate(RoomBase):
    """Schema for creating a room."""
    pass

class RoomRead(RoomBase):
    """Schema for reading a room."""
    id: int
    cinema_id: int
    created_at: datetime

class SeatBase(SQLModel):
    """Base model for Seat with shared fields."""
    row_label: str = Field(max_length=10)
    seat_number: int
    seat_type: str = Field(default="standard", max_length=50)

class SeatCreate(SeatBase):
    """Schema for creating a seat."""
    pass

class SeatRead(SeatBase):
    """Schema for reading a seat."""
    id: int
    room_id: int

class SeatBulkCreate(SQLModel):
    """Schema for bulk creating seats."""
    rows: int = Field(gt=0, description="Number of rows (e.g., 10 for rows A-J)")
    seats_per_row: int = Field(gt=0, description="Number of seats per row")
    seat_type: str = Field(default="standard", max_length=50)
