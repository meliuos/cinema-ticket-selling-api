"""Utility modules."""

from app.utils.email import (
    send_email,
    generate_movie_available_email,
    generate_test_email,
    EmailData,
)

__all__ = [
    "send_email",
    "generate_movie_available_email",
    "generate_test_email",
    "EmailData",
]
