from typing import Optional
from datetime import datetime, timezone
from sqlmodel import SQLModel, Field
from sqlalchemy import UniqueConstraint


class MovieNotification(SQLModel, table=True):
    """MovieNotification model - tracks user subscriptions for movie availability notifications."""
    __tablename__ = "movie_notification"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    movie_id: int = Field(foreign_key="movie.id", index=True)
    notified: bool = Field(default=False)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    notified_at: Optional[datetime] = Field(default=None)
    
    __table_args__ = (
        UniqueConstraint("user_id", "movie_id", name="uq_user_movie_notification"),
    )
