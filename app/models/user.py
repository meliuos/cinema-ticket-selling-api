from typing import Optional
from datetime import datetime, timezone
from sqlmodel import SQLModel, Field


class User(SQLModel, table=True):
    """User model - represents users table in database."""
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True, max_length=255)
    full_name: str = Field(max_length=255)
    hashed_password: str
    is_active: bool = Field(default=True)
    is_admin: bool = Field(default=False)  
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    date_of_birth: Optional[datetime] = None
    profile_picture_url: Optional[str] = Field(None, max_length=500)

    # Password reset fields
    reset_token: Optional[str] = Field(None, max_length=255)
    reset_token_expiry: Optional[datetime] = None

    # Preferences
    dark_mode: bool = Field(default=False)
    notifications_enabled: bool = Field(default=True)
    newsletter_subscribed: bool = Field(default=False)
