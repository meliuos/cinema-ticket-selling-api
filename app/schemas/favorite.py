"""Schemas for favorites."""

from datetime import datetime
from pydantic import BaseModel


class FavoriteCreate(BaseModel):
    """Schema for creating a favorite (cinema_id from path param)."""
    pass


class FavoriteRead(BaseModel):
    """Schema for reading a favorite."""
    id: int
    user_id: int
    cinema_id: int
    created_at: datetime

    class Config:
        from_attributes = True
