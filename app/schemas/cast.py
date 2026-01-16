"""Pydantic schemas for Cast-related API operations."""

from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field


class CastBase(SQLModel):
    """Base model for Cast with shared fields."""
    character_name: str = Field(max_length=255)  # Character name
    role: str = Field(max_length=255)  # Role description
    actor_name: str = Field(max_length=255)  # Real actor name
    profile_image_url: Optional[str] = Field(default=None, max_length=500)
    is_lead: bool = Field(default=False)
    order: int = Field(default=0)


class CastCreate(CastBase):
    """Schema for creating a cast member."""
    movie_id: int


class CastUpdate(SQLModel):
    """Schema for updating a cast member - all fields optional."""
    character_name: Optional[str] = Field(default=None, max_length=255)
    role: Optional[str] = Field(default=None, max_length=255)
    actor_name: Optional[str] = Field(default=None, max_length=255)
    profile_image_url: Optional[str] = Field(default=None, max_length=500)
    is_lead: Optional[bool] = None
    order: Optional[int] = None


class CastRead(CastBase):
    """Schema for reading a cast member - includes id and timestamps."""
    id: int
    movie_id: int
    created_at: datetime
    updated_at: datetime
