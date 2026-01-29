from pydantic import BaseModel
from datetime import datetime


class MovieNotificationBase(BaseModel):
    """Base schema for movie notifications."""
    movie_id: int


class MovieNotificationCreate(MovieNotificationBase):
    """Schema for creating a movie notification subscription."""
    pass


class MovieNotificationResponse(BaseModel):
    """Response schema for notification subscription."""
    subscribed: bool
    message: str


class MovieNotificationDetail(MovieNotificationBase):
    """Detailed movie notification schema."""
    id: int
    user_id: int
    notified: bool
    created_at: datetime
    notified_at: datetime | None
    
    class Config:
        from_attributes = True
