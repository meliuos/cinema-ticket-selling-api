"""Favorite routes for user's favorite cinemas."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List

from app.config import settings
from app.database import get_session
from app.models.favorite import Favorite
from app.models.cinema import Cinema
from app.models.user import User
from app.schemas.favorite import FavoriteRead
from app.schemas.cinema import CinemaRead
from app.services.auth import get_current_active_user

router = APIRouter(prefix=f"{settings.API_V1_PREFIX}/cinemas", tags=["Favorites"])


@router.post("/{cinema_id}/favorite", response_model=FavoriteRead, status_code=status.HTTP_201_CREATED)
def add_cinema_to_favorites(
    cinema_id: int,
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    """Add a cinema to user's favorites."""
    # Check if cinema exists
    cinema = session.get(Cinema, cinema_id)
    if not cinema:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cinema with id {cinema_id} not found"
        )
    
    # Check if already favorited
    existing_favorite = session.exec(
        select(Favorite).where(
            Favorite.user_id == current_user.id,
            Favorite.cinema_id == cinema_id
        )
    ).first()
    
    if existing_favorite:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cinema already in favorites"
        )
    
    # Create favorite
    favorite = Favorite(user_id=current_user.id, cinema_id=cinema_id)
    session.add(favorite)
    session.commit()
    session.refresh(favorite)
    return favorite


@router.delete("/{cinema_id}/favorite", status_code=status.HTTP_204_NO_CONTENT)
def remove_cinema_from_favorites(
    cinema_id: int,
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    """Remove a cinema from user's favorites."""
    # Find the favorite
    favorite = session.exec(
        select(Favorite).where(
            Favorite.user_id == current_user.id,
            Favorite.cinema_id == cinema_id
        )
    ).first()
    
    if not favorite:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cinema not in favorites"
        )
    
    session.delete(favorite)
    session.commit()
    return None


@router.get("/favorites", response_model=List[CinemaRead], tags=["Favorites"])
def get_user_favorite_cinemas(
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    """Get all favorite cinemas for the current user."""
    # Get user's favorite cinema IDs
    favorites = session.exec(
        select(Favorite).where(Favorite.user_id == current_user.id)
    ).all()
    
    cinema_ids = [fav.cinema_id for fav in favorites]
    
    if not cinema_ids:
        return []
    
    # Get the actual cinemas
    cinemas = session.exec(
        select(Cinema).where(Cinema.id.in_(cinema_ids))
    ).all()
    
    return cinemas
