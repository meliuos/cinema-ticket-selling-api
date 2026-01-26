"""Pydantic schemas for Review-related API operations."""

from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field


class ReviewBase(SQLModel):
    """Base model for Review with shared fields."""
    rating: int = Field(ge=1, le=5, description="Rating from 1 to 5 stars")
    title: Optional[str] = Field(None, max_length=255)
    comment: Optional[str] = Field(None, max_length=2000)


class ReviewCreate(SQLModel):
    """Schema for creating a new review."""
    rating: int = Field(ge=1, le=5, description="Rating from 1 to 5 stars")
    title: Optional[str] = Field(None, max_length=255)
    comment: Optional[str] = Field(None, max_length=2000)


class ReviewRead(ReviewBase):
    """Schema for reading a review - includes id and metadata."""
    id: int
    user_id: int
    movie_id: int
    reviewerName: str  
    reviewerAvatar: Optional[str] = None  # User's profile picture URL
    likes: int = 0
    dislikes: int = 0
    created_at: datetime
    updated_at: datetime


class ReviewUpdate(SQLModel):
    """Schema for updating a review."""
    rating: Optional[int] = Field(None, ge=1, le=5)
    title: Optional[str] = Field(None, max_length=255)
    comment: Optional[str] = Field(None, max_length=2000)


class ReviewReaction(SQLModel):
    """Schema for reacting to a review."""
    reaction_type: str = Field(description="Either 'like' or 'dislike'")


class ReviewReactionResponse(SQLModel):
    """Schema for reaction response."""
    message: str
    review: ReviewRead
    user_reaction: Optional[str] = None  # Current user's reaction: 'like', 'dislike', or None


class ReviewSummary(SQLModel):
    """Schema for review summary with rating breakdown."""
    movie_id: int
    total_reviews: int
    average_rating: float
    rating_breakdown: dict  # {1: count, 2: count, 3: count, 4: count, 5: count}


class ReviewListResponse(SQLModel):
    """Schema for paginated review list."""
    reviews: list[ReviewRead]
    total: int
    page: int
    page_size: int
    has_more: bool
