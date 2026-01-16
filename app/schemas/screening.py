"""Pydantic schemas for Screening-related API operations."""
from datetime import datetime, date
from typing import List
from sqlmodel import SQLModel, Field
from app.schemas.movie import MovieRead
from app.schemas.cinema import RoomWithCinemaRead


class ScreeningBase(SQLModel):
    """Base model for Screening with shared fields."""
    movie_id: int
    room_id: int
    screening_time: datetime
    price: float = Field(gt=0)


class ScreeningCreate(ScreeningBase):
    """Schema for creating a screening."""
    pass


class ScreeningRead(ScreeningBase):
    """Schema for reading a screening."""
    id: int
    created_at: datetime
class ScreeningReadDetailed(SQLModel):
    id: int
    screening_time: datetime
    price: float
    movie: MovieRead
    room: RoomWithCinemaRead


class ScreeningReadEnhanced(SQLModel):
    """Enhanced schema for reading a screening with additional details."""
    id: int
    movie_id: int
    room_name: str
    screening_time: datetime
    screening_date: date
    price: float
    available_seats_count: int
    created_at: datetime


class ShowtimeDetail(SQLModel):
    """Schema for showtime detail with ID and time."""
    id: int
    screening_time: datetime


class MovieShowtimesRead(SQLModel):
    movie: MovieRead
    price: float
    showtimes: List[ShowtimeDetail]
