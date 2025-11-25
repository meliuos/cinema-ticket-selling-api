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
