"""Screening routes."""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session, select
from sqlalchemy.orm import selectinload
from typing import List, Optional
from datetime import datetime, date

from app.config import settings
from app.database import get_session
from app.models.movie import Movie, MovieState
from app.models.cinema import Room, Seat
from app.models.screening import Screening
from app.models.user import User
from app.models.cast import Cast
from app.schemas.screening import ScreeningCreate, ScreeningRead, ScreeningReadDetailed
from app.schemas.cinema import SeatRead
from app.services.cinema import get_available_seats
from app.services.auth import get_current_admin_user

router = APIRouter(prefix=f"{settings.API_V1_PREFIX}/screenings", tags=["Screenings"])


@router.post(
    "/",
    response_model=ScreeningRead,
    status_code=status.HTTP_201_CREATED
)
def create_screening(
    screening: ScreeningCreate,
    session: Session = Depends(get_session),
    current_admin: User = Depends(get_current_admin_user)
):
    """Create a new screening (showtime) (admin only)."""
    # Verify movie exists
    movie = session.get(Movie, screening.movie_id)
    if not movie:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Movie with id {screening.movie_id} not found"
        )
    
    # Block screening creation for coming soon movies 
    if movie.state == MovieState.COMING_SOON:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot create screenings for coming soon movies"
        )
    
    # Verify room exists
    room = session.get(Room, screening.room_id)
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Room with id {screening.room_id} not found"
        )
    
    db_screening = Screening.model_validate(screening)
    session.add(db_screening)
    session.commit()
    session.refresh(db_screening)
    return db_screening


@router.get("/", response_model=List[ScreeningRead])
def list_screenings(
    movie_id: Optional[int] = Query(None, description="Filter by movie ID"),
    room_id: Optional[int] = Query(None, description="Filter by room ID"),
    cinema_id: Optional[int] = Query(None, description="Filter by cinema ID"),
    date: Optional[date] = Query(None, description="Filter by date (YYYY-MM-DD)"),
    skip: int = 0,
    limit: int = 100,
    session: Session = Depends(get_session)
):
    """List screenings with optional filters."""
    query = select(Screening)
    
    if movie_id:
        query = query.where(Screening.movie_id == movie_id)
    
    if room_id:
        query = query.where(Screening.room_id == room_id)
    
    if cinema_id:
        # Join with Room to filter by cinema
        query = query.join(Room).where(Room.cinema_id == cinema_id)
    
    if date:
        # Filter by date (screening_time on the given date)
        start_of_day = datetime.combine(date, datetime.min.time())
        end_of_day = datetime.combine(date, datetime.max.time())
        query = query.where(
            Screening.screening_time >= start_of_day,
            Screening.screening_time <= end_of_day
        )
    
    screenings = session.exec(query.offset(skip).limit(limit)).all()
    return screenings


@router.get("/{screening_id}", response_model=ScreeningReadDetailed)
def get_screening(screening_id: int, session: Session = Depends(get_session)):
    """Get a specific screening by ID."""
    screening = session.exec(
        select(Screening)
        .where(Screening.id == screening_id)
        .options(
            selectinload(Screening.movie),
            selectinload(Screening.room).selectinload(Room.cinema)
        )
    ).first()
    
    if not screening:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Screening with id {screening_id} not found"
        )
    
    # Get cast details for the movie
    cast_statement = select(Cast).where(Cast.movie_id == screening.movie_id).order_by(Cast.order)
    casts = session.exec(cast_statement).all()
    
    # Convert to dict and normalize
    screening_dict = screening.model_dump()
    movie_dict = screening.movie.model_dump()
    room_dict = screening.room.model_dump()
    cinema_dict = screening.room.cinema.model_dump() if screening.room.cinema else None
    
    # Normalize genre
    if isinstance(movie_dict.get('genre'), str):
        movie_dict['genre'] = [movie_dict['genre']] if movie_dict['genre'] else None
    
    # Add cast details to movie
    movie_dict['cast'] = [cast.actor_name for cast in casts]
    
    # Add cinema to room
    room_dict['cinema'] = cinema_dict
    
    # Build final response
    screening_dict['movie'] = movie_dict
    screening_dict['room'] = room_dict
    
    return screening_dict


@router.get("/{screening_id}/available-seats", response_model=List[SeatRead])
def get_screening_available_seats(screening_id: int, session: Session = Depends(get_session)):
    """Get available seats for a screening."""
    available_seats = get_available_seats(session, screening_id)
    return available_seats
