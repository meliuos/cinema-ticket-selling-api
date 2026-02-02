"""Movie favorite routes for user's favorite movies."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List

from app.config import settings
from app.database import get_session
from app.models.favorite import Favorite
from app.models.movie import Movie
from app.models.user import User
from app.schemas.favorite import FavoriteRead
from app.schemas.movie import MovieRead
from app.services.auth import get_current_active_user

router = APIRouter(prefix=f"{settings.API_V1_PREFIX}/movies", tags=["Movie Favorites"])


@router.post("/{movie_id}/favorite", response_model=FavoriteRead, status_code=status.HTTP_201_CREATED)
def add_movie_to_favorites(
    movie_id: int,
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    """Add a movie to user's favorites."""
    # Check if movie exists
    movie = session.get(Movie, movie_id)
    if not movie:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Movie with id {movie_id} not found"
        )

    # Check if already favorited
    existing_favorite = session.exec(
        select(Favorite).where(
            Favorite.user_id == current_user.id,
            Favorite.movie_id == movie_id
        )
    ).first()

    if existing_favorite:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Movie already in favorites"
        )

    # Create favorite
    favorite = Favorite(user_id=current_user.id, movie_id=movie_id)
    session.add(favorite)
    session.commit()
    session.refresh(favorite)
    return favorite


@router.delete("/{movie_id}/favorite", status_code=status.HTTP_204_NO_CONTENT)
def remove_movie_from_favorites(
    movie_id: int,
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    """Remove a movie from user's favorites."""
    # Find the favorite
    favorite = session.exec(
        select(Favorite).where(
            Favorite.user_id == current_user.id,
            Favorite.movie_id == movie_id
        )
    ).first()

    if not favorite:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Movie not in favorites"
        )

    session.delete(favorite)
    session.commit()
    return None


@router.get("/favorites", response_model=List[MovieRead], tags=["Movie Favorites"])
def get_user_favorite_movies(
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    """Get all favorite movies for the current user."""
    # Get user's favorite movie IDs
    favorites = session.exec(
        select(Favorite).where(
            Favorite.user_id == current_user.id,
            Favorite.movie_id.isnot(None)
        )
    ).all()

    movie_ids = [fav.movie_id for fav in favorites]

    if not movie_ids:
        return []

    # Get the actual movies
    movies = session.exec(
        select(Movie).where(Movie.id.in_(movie_ids))
    ).all()

    return movies
