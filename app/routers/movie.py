"""Movie routes."""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session, select, or_
from typing import List, Optional
from datetime import datetime, date

from app.config import settings
from app.database import get_session
from app.models.movie import Movie
from app.models.screening import Screening
from app.models.user import User
from app.schemas.movie import MovieCreate, MovieRead, MovieUpdate
from app.schemas.screening import ScreeningRead
from app.services.auth import get_current_admin_user

router = APIRouter(prefix=f"{settings.API_V1_PREFIX}/movies", tags=["Movies"])


@router.post(
    "/",
    response_model=MovieRead,
    status_code=status.HTTP_201_CREATED
)
def create_movie(
    movie: MovieCreate,
    session: Session = Depends(get_session),
    current_admin: User = Depends(get_current_admin_user)
):
    """Create a new movie with comprehensive details (admin only)."""
    db_movie = Movie.model_validate(movie)
    session.add(db_movie)
    session.commit()
    session.refresh(db_movie)
    return db_movie


@router.get("/", response_model=List[MovieRead])
def list_movies(
    skip: int = 0,
    limit: int = 100,
    session: Session = Depends(get_session)
):
    """List all movies."""
    movies = session.exec(select(Movie).offset(skip).limit(limit)).all()
    return movies


@router.get("/search", response_model=List[MovieRead])
def search_movies(
    q: str = Query(..., min_length=1, description="Search query for movie title, genre, cast, or director"),
    skip: int = 0,
    limit: int = 100,
    session: Session = Depends(get_session)
):
    """Search movies by title, genre, cast, or director."""
    search_term = f"%{q.lower()}%"
    
    # Search across multiple fields
    statement = select(Movie).where(
        or_(
            Movie.title.ilike(search_term),
            Movie.genre.ilike(search_term),
            Movie.director.ilike(search_term),
            Movie.description.ilike(search_term)
        )
    ).offset(skip).limit(limit)
    
    movies = session.exec(statement).all()
    return movies


@router.get("/{movie_id}", response_model=MovieRead)
def get_movie(movie_id: int, session: Session = Depends(get_session)):
    """Get a specific movie by ID."""
    movie = session.get(Movie, movie_id)
    if not movie:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Movie with id {movie_id} not found"
        )
    return movie


@router.get("/{movie_id}/cast", response_model=List[str])
def get_movie_cast(movie_id: int, session: Session = Depends(get_session)):
    """Get the cast list for a specific movie."""
    movie = session.get(Movie, movie_id)
    if not movie:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Movie with id {movie_id} not found"
        )
    return movie.cast or []


@router.get("/{movie_id}/showtimes", response_model=List[ScreeningRead])
def get_movie_showtimes(
    movie_id: int,
    date: Optional[date] = Query(None, description="Filter by date (YYYY-MM-DD)"),
    skip: int = 0,
    limit: int = 100,
    session: Session = Depends(get_session)
):
    """Get all showtimes for a specific movie, optionally filtered by date."""
    # Check if movie exists
    movie = session.get(Movie, movie_id)
    if not movie:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Movie with id {movie_id} not found"
        )
    
    # Build query
    query = select(Screening).where(Screening.movie_id == movie_id)
    
    if date:
        # Filter by date
        start_of_day = datetime.combine(date, datetime.min.time())
        end_of_day = datetime.combine(date, datetime.max.time())
        query = query.where(
            Screening.screening_time >= start_of_day,
            Screening.screening_time <= end_of_day
        )
    
    # Order by screening time
    query = query.order_by(Screening.screening_time)
    
    screenings = session.exec(query.offset(skip).limit(limit)).all()
    return screenings


@router.patch("/{movie_id}", response_model=MovieRead)
def update_movie(
    movie_id: int,
    movie_update: MovieUpdate,
    session: Session = Depends(get_session),
    current_admin: User = Depends(get_current_admin_user)
):
    """Update a movie's information (admin only)."""
    db_movie = session.get(Movie, movie_id)
    if not db_movie:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Movie with id {movie_id} not found"
        )
    
    # Update only provided fields
    movie_data = movie_update.model_dump(exclude_unset=True)
    for key, value in movie_data.items():
        setattr(db_movie, key, value)
    
    db_movie.updated_at = datetime.utcnow()
    session.add(db_movie)
    session.commit()
    session.refresh(db_movie)
    return db_movie


@router.delete("/{movie_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_movie(
    movie_id: int,
    session: Session = Depends(get_session),
    current_admin: User = Depends(get_current_admin_user)
):
    """Delete a movie (admin only)."""
    movie = session.get(Movie, movie_id)
    if not movie:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Movie with id {movie_id} not found"
        )
    
    session.delete(movie)
    session.commit()
    return None
