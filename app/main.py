"""Main FastAPI application - Cinema Ticketing System."""

from fastapi import FastAPI, Request, status
from fastapi.staticfiles import StaticFiles
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from app.config import settings
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.database import create_db_and_tables
from app.services.background_tasks import background_manager

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
    cinema_favorites_router,
    movie_favorites_router,
    user_features_router,
    recommendation_router,
    admin_router,
    cast_router,
    payment_router,
)
origins = [
    "http://localhost:4200",]

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle application lifespan events."""
    # Startup
    create_db_and_tables()
    
    # Start background tasks
    import asyncio
    cleanup_task = asyncio.create_task(
        background_manager.start_cleanup_task(interval_minutes=1)
    )
    
    yield
    
    # Shutdown
    background_manager.stop_cleanup_task()
    cleanup_task.cancel()
    try:
        await cleanup_task
    except asyncio.CancelledError:
        pass

# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG,
    lifespan=lifespan
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for uploads
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


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
app.include_router(cinema_favorites_router)  # Must be before cinema_router to match /cinemas/favorites before /cinemas/{cinema_id}
app.include_router(movie_favorites_router)  
app.include_router(movie_router)
app.include_router(cinema_router)
app.include_router(seat_router)
app.include_router(seat_reservation_router) 
app.include_router(websocket_router)  
app.include_router(recommendation_router)
app.include_router(screening_router)
app.include_router(showtime_router)
app.include_router(ticket_router)
app.include_router(payment_router)  
app.include_router(user_router)
app.include_router(review_router)
app.include_router(user_features_router)
app.include_router(admin_router)
app.include_router(cast_router)

