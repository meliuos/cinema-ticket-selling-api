"""Business logic services for the cinema ticketing system."""

from app.services.auth import (
    verify_password,
    get_password_hash,
    create_access_token,
    authenticate_user,
    get_current_user,
    get_current_active_user,
    oauth2_scheme,
)
from app.services.cinema import (
    bulk_create_seats,
    get_available_seats,
    book_tickets,
    cancel_ticket,
)

__all__ = [
    # Auth
    "verify_password",
    "get_password_hash",
    "create_access_token",
    "authenticate_user",
    "get_current_user",
    "get_current_active_user",
    "oauth2_scheme",
    # Cinema
    "bulk_create_seats",
    "get_available_seats",
    "book_tickets",
    "cancel_ticket",
]
