"""TokenBlacklist model for tracking revoked JWT tokens."""

from typing import Optional
from datetime import datetime, timezone
from sqlmodel import SQLModel, Field


class TokenBlacklist(SQLModel, table=True):
    """TokenBlacklist model - stores revoked JWT tokens for logout functionality."""
    id: Optional[int] = Field(default=None, primary_key=True)
    token_jti: str = Field(unique=True, index=True, max_length=255)  # JWT ID (jti claim)
    user_id: int = Field(foreign_key="user.id", index=True)
    expires_at: datetime  # When the token naturally expires
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))  # When it was blacklisted
