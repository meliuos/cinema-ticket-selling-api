"""Movie routes."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List
from datetime import datetime

from app.config import settings
from app.database import get_session
from app.models.movie import Movie
from app.schemas.movie import MovieCreate, MovieRead, MovieUpdate

router = APIRouter(prefix=f"{settings.API_V1_PREFIX}/movies", tags=["Movies"])


@router.post(
    "/",
    response_model=MovieRead,
    status_code=status.HTTP_201_CREATED
)
def create_movie(movie: MovieCreate, session: Session = Depends(get_session)):
    """Create a new movie with comprehensive details."""
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


@router.patch("/{movie_id}", response_model=MovieRead)
def update_movie(
    movie_id: int,
    movie_update: MovieUpdate,
    session: Session = Depends(get_session)
):
    """Update a movie's information."""
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
def delete_movie(movie_id: int, session: Session = Depends(get_session)):
    """Delete a movie."""
    movie = session.get(Movie, movie_id)
    if not movie:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Movie with id {movie_id} not found"
        )
    
    session.delete(movie)
    session.commit()
    return None
