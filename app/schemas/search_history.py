"""Schemas for search history."""

from datetime import datetime
from pydantic import BaseModel


class SearchHistoryRead(BaseModel):
    """Schema for reading search history."""
    id: int
    user_id: int
    search_query: str
    search_type: str
    created_at: datetime

    class Config:
        from_attributes = True
