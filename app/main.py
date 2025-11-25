"""Main FastAPI application - Cinema Ticketing System."""

from fastapi import FastAPI
from app.config import settings
from app.database import create_db_and_tables
from app.routers import (
    auth_router,
    cinema_router,
    seat_router,
    movie_router,
    screening_router,
    ticket_router,
)

# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG,
)


@app.on_event("startup")
def on_startup():
    """Initialize database tables on application startup."""
    create_db_and_tables()


@app.get("/")
def read_root():
    """Root endpoint - health check."""
    return {
        "message": "Welcome to FastAPI Cinema Ticketing System!",
        "status": "healthy",
        "docs": "/docs"
    }


# Include all routers
app.include_router(auth_router)
app.include_router(cinema_router)
app.include_router(seat_router)
app.include_router(movie_router)
app.include_router(screening_router)
app.include_router(ticket_router)
