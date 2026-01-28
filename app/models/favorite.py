"""Favorite model for user's favorite cinemas and movies."""

from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field


class Favorite(SQLModel, table=True):
    """Favorite model - represents user's favorite cinemas and movies."""
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    cinema_id: Optional[int] = Field(default=None, foreign_key="cinema.id", index=True)
    movie_id: Optional[int] = Field(default=None, foreign_key="movie.id", index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        # Ensure user can't favorite same cinema/movie twice
        unique_together = [("user_id", "cinema_id"), ("user_id", "movie_id")]
