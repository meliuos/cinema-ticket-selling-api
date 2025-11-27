from typing import Optional, List, Dict, Any
from datetime import datetime, date
from sqlmodel import SQLModel, Field, Column
from sqlalchemy import JSON


class Movie(SQLModel, table=True):
    """Movie model - represents movies with comprehensive details."""
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Basic Information
    title: str = Field(max_length=255)
    description: Optional[str] = Field(default=None, max_length=2000)
    duration_minutes: int = Field(gt=0)
    genre: Optional[List[str]] = Field(default=None, sa_column=Column(JSON))  
    rating: Optional[str] = Field(default=None, max_length=10)  # e.g., "PG-13", "R"
    
    cast: Optional[List[str]] = Field(default=None, sa_column=Column(JSON))  # List of actor names
    director: Optional[str] = Field(default=None, max_length=255)
    writers: Optional[List[str]] = Field(default=None, sa_column=Column(JSON))
    producers: Optional[List[str]] = Field(default=None, sa_column=Column(JSON))
    
    # Release Information
    release_date: Optional[date] = Field(default=None)
    country: Optional[str] = Field(default=None, max_length=100)
    language: Optional[str] = Field(default=None, max_length=100)
    
    # Financial Information
    budget: Optional[float] = Field(default=None, ge=0)  # in USD
    revenue: Optional[float] = Field(default=None, ge=0)  # in USD
    
    # Production
    production_company: Optional[str] = Field(default=None, max_length=255)
    distributor: Optional[str] = Field(default=None, max_length=255)
    
    # Media & Awards
    image_url: Optional[str] = Field(default=None, max_length=500)
    trailer_url: Optional[str] = Field(default=None, max_length=500)
    awards: Optional[List[str]] = Field(default=None, sa_column=Column(JSON))
    
    # Additional Details (JSON field for any other metadata)
    details: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
