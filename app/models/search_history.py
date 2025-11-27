"""Search history model for tracking user searches."""

from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field


class SearchHistory(SQLModel, table=True):
    """SearchHistory model - represents user's recent searches."""
    __tablename__ = "search_history"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    search_query: str = Field(max_length=255)
    search_type: str = Field(max_length=50)  # 'movie', 'cinema', 'general'
    created_at: datetime = Field(default_factory=datetime.utcnow)
