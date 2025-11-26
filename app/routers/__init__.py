"""API routers for the cinema ticketing system."""

from app.routers.auth import router as auth_router
from app.routers.cinema import router as cinema_router
from app.routers.seat import router as seat_router
from app.routers.movie import router as movie_router
from app.routers.screening import router as screening_router
from app.routers.ticket import router as ticket_router
from app.routers.user import router as user_router

__all__ = [
    "auth_router",
    "cinema_router",
    "seat_router",
    "movie_router",
    "screening_router",
    "ticket_router",
    "user_router",
]
