from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field


class Screening(SQLModel, table=True):
    """Screening model - represents movie showtimes."""
    id: Optional[int] = Field(default=None, primary_key=True)
    movie_id: int = Field(foreign_key="movie.id")
    room_id: int = Field(foreign_key="room.id")
    screening_time: datetime
    price: float = Field(gt=0)
    created_at: datetime = Field(default_factory=datetime.utcnow)
