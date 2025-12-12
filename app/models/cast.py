"""Cast model - represents actors/crew members in movies."""

from typing import Optional
from datetime import datetime, date
from sqlmodel import SQLModel, Field


class Cast(SQLModel, table=True):
    """Cast model - represents cast members for movies."""
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Basic Information
    name: str = Field(max_length=255)
    role: str = Field(max_length=255)  # Character name or role in the movie
    
    # Relationship
    movie_id: int = Field(foreign_key="movie.id", index=True)
    
    # Actor details
    actor_name: str = Field(max_length=255)  # Real name of the actor
    profile_image_url: Optional[str] = Field(default=None, max_length=500)
    
    # Additional info
    is_lead: bool = Field(default=False)  # Whether this is a lead role
    order: int = Field(default=0)  # Display order in cast list
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
