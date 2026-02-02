from typing import Optional
from sqlmodel import SQLModel, Field


class FAQ(SQLModel, table=True):
    """FAQ model - represents faqs table in database."""
    id: Optional[int] = Field(default=None, primary_key=True)
    question: str = Field(nullable=False)
    answer: str = Field(nullable=False)