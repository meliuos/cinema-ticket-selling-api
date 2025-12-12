"""Cast routes for movie cast members."""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from datetime import datetime

from app.config import settings
from app.database import get_session
from app.models.cast import Cast
from app.models.movie import Movie
from app.schemas.cast import CastCreate, CastRead, CastUpdate

router = APIRouter(prefix=f"{settings.API_V1_PREFIX}/casts", tags=["Casts"])


@router.post("/", response_model=CastRead, status_code=status.HTTP_201_CREATED)
def create_cast(cast: CastCreate, session: Session = Depends(get_session)):
    """Create a new cast member for a movie."""
    # Verify movie exists
    movie = session.get(Movie, cast.movie_id)
    if not movie:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Movie not found"
        )
    
    db_cast = Cast.model_validate(cast)
    session.add(db_cast)
    session.commit()
    session.refresh(db_cast)
    return db_cast


@router.get("/", response_model=List[CastRead])
def get_all_casts(
    skip: int = 0,
    limit: int = 100,
    session: Session = Depends(get_session)
):
    """Get all cast members."""
    statement = select(Cast).offset(skip).limit(limit)
    casts = session.exec(statement).all()
    return casts


@router.get("/{cast_id}", response_model=CastRead)
def get_cast(cast_id: int, session: Session = Depends(get_session)):
    """Get a specific cast member by ID."""
    cast = session.get(Cast, cast_id)
    if not cast:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cast member not found"
        )
    return cast


@router.get("/movie/{movie_id}", response_model=List[CastRead])
def get_movie_cast(movie_id: int, session: Session = Depends(get_session)):
    """Get all cast members for a specific movie."""
    # Verify movie exists
    movie = session.get(Movie, movie_id)
    if not movie:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Movie not found"
        )
    
    statement = select(Cast).where(Cast.movie_id == movie_id).order_by(Cast.order)
    casts = session.exec(statement).all()
    return casts


@router.put("/{cast_id}", response_model=CastRead)
def update_cast(
    cast_id: int,
    cast_update: CastUpdate,
    session: Session = Depends(get_session)
):
    """Update a cast member."""
    db_cast = session.get(Cast, cast_id)
    if not db_cast:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cast member not found"
        )
    
    cast_data = cast_update.model_dump(exclude_unset=True)
    for key, value in cast_data.items():
        setattr(db_cast, key, value)
    
    db_cast.updated_at = datetime.utcnow()
    session.add(db_cast)
    session.commit()
    session.refresh(db_cast)
    return db_cast


@router.delete("/{cast_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_cast(cast_id: int, session: Session = Depends(get_session)):
    """Delete a cast member."""
    cast = session.get(Cast, cast_id)
    if not cast:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cast member not found"
        )
    
    session.delete(cast)
    session.commit()
    return None
