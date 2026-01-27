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


class ShowtimeDetail(SQLModel):
    """Schema for showtime details in movie showtimes."""
    id: int
    screening_time: datetime
    price: float
    room: RoomWithCinemaRead


class MovieShowtimesRead(SQLModel):
    movie: MovieRead
    price: float
    showtimes: List[ShowtimeDetail]
