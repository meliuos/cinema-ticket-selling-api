"""Favorite model for user's favorite cinemas."""

from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field


class Favorite(SQLModel, table=True):
    """Favorite model - represents user's favorite cinemas."""
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    cinema_id: int = Field(foreign_key="cinema.id", index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        # Ensure user can't favorite same cinema twice
        unique_together = [("user_id", "cinema_id")]
