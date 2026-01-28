"""Main FastAPI application - Cinema Ticketing System."""
from fastapi.middleware.cors import CORSMiddleware

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.config import settings
from fastapi.middleware.cors import CORSMiddleware
from app.database import create_db_and_tables
from app.routers import (
    auth_router,
    cinema_router,
    seat_router,
    seat_reservation_router,
    websocket_router,
    movie_router,
    screening_router,
    showtime_router,
    ticket_router,
    user_router,
    review_router,
    favorite_router,
    user_features_router,
    recommendation_router,
    admin_router,
    cast_router,
)
origins = [
    "http://localhost:4200",
    "http://localhost:52970",
    "http://localhost:3000",
    "http://localhost:8080",
    "http://localhost",
    "http://127.0.0.1",
]

# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG,
)

# Add CORS middleware FIRST (must be before other middleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for uploads
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # you can restrict this later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
app.include_router(favorite_router)  # Must be before cinema_router to match /cinemas/favorites before /cinemas/{cinema_id}
app.include_router(cinema_router)
app.include_router(seat_router)
app.include_router(seat_reservation_router)
app.include_router(websocket_router)
app.include_router(recommendation_router)  # Must be before movie_router to match /movies/recommended before /movies/{movie_id}
app.include_router(movie_router)
app.include_router(screening_router)
app.include_router(showtime_router)
app.include_router(ticket_router)
app.include_router(user_router)
app.include_router(review_router)
app.include_router(user_features_router)
app.include_router(admin_router)
app.include_router(cast_router)

