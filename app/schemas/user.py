"""Pydantic schemas for User-related API operations."""

from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field


class UserBase(SQLModel):
    """Base model for User with shared fields."""
    email: str = Field(max_length=255)
    full_name: str = Field(max_length=255)
    is_active: bool = Field(default=True)


class UserCreate(SQLModel):
    """Schema for creating a new user."""
    email: str = Field(max_length=255)
    password: str = Field(min_length=8)
    full_name: str = Field(max_length=255)


class UserRead(UserBase):
    """Schema for reading a user - includes id but excludes password."""
    id: int
    created_at: datetime
    updated_at: datetime
    date_of_birth: Optional[datetime] = None
    profile_picture_url: Optional[str] = None
    is_admin: bool = Field(default=False)
    dark_mode: bool = Field(default=False)
    notifications_enabled: bool = Field(default=True)
    newsletter_subscribed: bool = Field(default=False)


class UserUpdate(SQLModel):
    """Schema for updating user profile."""
    full_name: Optional[str] = Field(None, max_length=255)
    email: Optional[str] = Field(None, max_length=255)
    date_of_birth: Optional[datetime] = None


class UserPreferences(SQLModel):
    """Schema for user preferences."""
    dark_mode: bool = Field(default=False)
    notifications_enabled: bool = Field(default=True)
    newsletter_subscribed: bool = Field(default=False)


class UserPreferencesUpdate(SQLModel):
    """Schema for updating user preferences."""
    dark_mode: Optional[bool] = None
    notifications_enabled: Optional[bool] = None
    newsletter_subscribed: Optional[bool] = None


class UserLogin(SQLModel):
    """Schema for user login."""
    email: str
    password: str


class Token(SQLModel):
    """Schema for token response."""
    access_token: str
    token_type: str


class TokenData(SQLModel):
    """Schema for token payload data."""
    email: Optional[str] = None


class EmailCheckResponse(SQLModel):
    """Schema for email check response."""
    email: str
    exists: bool


class RefreshTokenRequest(SQLModel):
    """Schema for refresh token request."""
    token: str


class ForgotPasswordRequest(SQLModel):
    """Schema for forgot password request."""
    email: str = Field(max_length=255)


class ResetPasswordRequest(SQLModel):
    """Schema for reset password request."""
    token: str
    new_password: str = Field(min_length=8)


class ChangePasswordRequest(SQLModel):
    """Schema for change password request."""
    current_password: str
    new_password: str = Field(min_length=8)


class PasswordResetResponse(SQLModel):
    """Schema for password reset token response (simulating email)."""
    message: str
    reset_token: str  # In production, this would be sent via email
    expires_in_minutes: int

