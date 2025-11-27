from typing import Optional, List
from datetime import datetime
from sqlmodel import SQLModel, Field, Column
from sqlalchemy import JSON


class Cinema(SQLModel, table=True):
    """Cinema model - represents cinema locations."""
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=255)
    address: str = Field(max_length=500)
    city: str = Field(max_length=100)
    longitude: Optional[float] = Field(default=None)  
    latitude: Optional[float] = Field(default=None)   
    imageurl: Optional[str] = Field(default=None, max_length=500)  
    phone: Optional[str] = Field(default=None, max_length=20)      
    hasParking: bool = Field(default=False)  
    isAccessible: bool = Field(default=False)  # Whether cinema is wheelchair accessible
    amenities: Optional[List[str]] = Field(default=None, sa_column=Column(JSON)) 
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Room(SQLModel, table=True):
    """Room model - represents cinema rooms/theaters."""
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=100)
    cinema_id: int = Field(foreign_key="cinema.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Seat(SQLModel, table=True):
    """Seat model - represents individual seats in a room."""
    id: Optional[int] = Field(default=None, primary_key=True)
    room_id: int = Field(foreign_key="room.id")
    row_label: str = Field(max_length=10)  # e.g., "A", "B", "C"
    seat_number: int  # e.g., 1, 2, 3
    seat_type: str = Field(default="standard", max_length=50)  # standard, vip, etc.
    
    class Config:
        # Ensure unique seat per room (row + number)
        table_args = {"unique_together": [("room_id", "row_label", "seat_number")]}
