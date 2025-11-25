"""Pydantic schemas for Movie-related API operations."""

from typing import Optional, List, Dict, Any
from datetime import datetime, date
from sqlmodel import SQLModel, Field


class MovieBase(SQLModel):
    """Base model for Movie with shared fields."""
    # Basic Information
    title: str = Field(max_length=255)
    description: Optional[str] = Field(default=None, max_length=2000)
    duration_minutes: int = Field(gt=0)
    genre: str = Field(max_length=100)
    rating: Optional[str] = Field(default=None, max_length=10)
    
    # Cast & Crew
    cast: Optional[List[str]] = None
    director: Optional[str] = Field(default=None, max_length=255)
    writers: Optional[List[str]] = None
    producers: Optional[List[str]] = None
    
    # Release Information
    release_date: Optional[date] = None
    country: Optional[str] = Field(default=None, max_length=100)
    language: Optional[str] = Field(default=None, max_length=100)
    
    # Financial Information
    budget: Optional[float] = Field(default=None, ge=0)
    revenue: Optional[float] = Field(default=None, ge=0)
    
    # Production
    production_company: Optional[str] = Field(default=None, max_length=255)
    distributor: Optional[str] = Field(default=None, max_length=255)
    
    # Media & Awards
    image_url: Optional[str] = Field(default=None, max_length=500)
    trailer_url: Optional[str] = Field(default=None, max_length=500)
    awards: Optional[List[str]] = None
    
    # Additional Details
    details: Optional[Dict[str, Any]] = None


class MovieCreate(MovieBase):
    """Schema for creating a movie."""
    pass


class MovieUpdate(SQLModel):
    """Schema for updating a movie - all fields optional."""
    title: Optional[str] = Field(default=None, max_length=255)
    description: Optional[str] = Field(default=None, max_length=2000)
    duration_minutes: Optional[int] = Field(default=None, gt=0)
    genre: Optional[str] = Field(default=None, max_length=100)
    rating: Optional[str] = Field(default=None, max_length=10)
    
    cast: Optional[List[str]] = None
    director: Optional[str] = Field(default=None, max_length=255)
    writers: Optional[List[str]] = None
    producers: Optional[List[str]] = None
    
    release_date: Optional[date] = None
    country: Optional[str] = Field(default=None, max_length=100)
    language: Optional[str] = Field(default=None, max_length=100)
    
    budget: Optional[float] = Field(default=None, ge=0)
    revenue: Optional[float] = Field(default=None, ge=0)
    
    production_company: Optional[str] = Field(default=None, max_length=255)
    distributor: Optional[str] = Field(default=None, max_length=255)
    
    image_url: Optional[str] = Field(default=None, max_length=500)
    trailer_url: Optional[str] = Field(default=None, max_length=500)
    awards: Optional[List[str]] = None
    
    details: Optional[Dict[str, Any]] = None


class MovieRead(MovieBase):
    """Schema for reading a movie - includes id and timestamps."""
    id: int
    created_at: datetime
    updated_at: datetime
