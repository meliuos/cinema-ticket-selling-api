"""Review model for movie reviews."""

from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship


class Review(SQLModel, table=True):
    """Review model - represents user reviews for movies."""
    __tablename__ = "reviews"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Foreign Keys
    user_id: int = Field(foreign_key="user.id", index=True)
    movie_id: int = Field(foreign_key="movie.id", index=True)
    
    # Review Content
    rating: int = Field(ge=1, le=5, description="Rating from 1 to 5 stars")
    title: Optional[str] = Field(default=None, max_length=255)
    comment: Optional[str] = Field(default=None, max_length=2000)
    
    # Engagement Metrics
    likes: int = Field(default=0, ge=0)
    dislikes: int = Field(default=0, ge=0)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Soft Delete
    is_deleted: bool = Field(default=False)


class ReviewReactionModel(SQLModel, table=True):
    """Model to track user reactions to reviews."""
    __tablename__ = "review_reactions"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Foreign Keys
    user_id: int = Field(foreign_key="user.id", index=True)
    review_id: int = Field(foreign_key="reviews.id", index=True)
    
    # Reaction Type: 'like' or 'dislike'
    reaction_type: str = Field(max_length=10)
    
    # Timestamp
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        # Ensure unique constraint: one user can only have one reaction per review
        indexes = [
            {"fields": ["user_id", "review_id"], "unique": True}
        ]
