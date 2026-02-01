"""Pydantic schemas for FAQ-related API operations."""

from pydantic import BaseModel


class FAQBase(BaseModel):
    """Base model for FAQ with shared fields."""
    question: str
    answer: str


class FAQ(FAQBase):
    """Schema for reading an FAQ - includes id."""
    id: int

    class Config:
        from_attributes = True