"""API routers for the cinema ticketing system."""

from app.routers.auth import router as auth_router
from app.routers.cinema import router as cinema_router
from app.routers.seat import router as seat_router
from app.routers.movie import router as movie_router
from app.routers.screening import router as screening_router
from app.routers.showtime import router as showtime_router
from app.routers.ticket import router as ticket_router
from app.routers.user import router as user_router
from app.routers.review import router as review_router
from app.routers.favorite import router as favorite_router
from app.routers.user_features import router as user_features_router, movie_router as recommendation_router
from app.routers.admin import router as admin_router
from app.routers.cast import router as cast_router

__all__ = [
    "auth_router",
    "cinema_router",
    "seat_router",
    "movie_router",
    "screening_router",
    "showtime_router",
    "ticket_router",
    "user_router",
    "review_router",
    "favorite_router",
    "user_features_router",
    "recommendation_router",
    "admin_router",
    "cast_router",
]

