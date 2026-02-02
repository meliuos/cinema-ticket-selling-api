"""Screening routes."""

from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from sqlmodel import Session, select
from sqlalchemy.orm import selectinload
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
from app.services.notification import NotificationService

router = APIRouter(prefix=f"{settings.API_V1_PREFIX}/screenings", tags=["Screenings"])


@router.post(
    "/",
    response_model=ScreeningRead,
    status_code=status.HTTP_201_CREATED
)
async def create_screening(
    screening: ScreeningCreate,
    background_tasks: BackgroundTasks,
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
    
    # Track if this is the first screening for a COMING_SOON movie
    was_coming_soon = movie.state == MovieState.COMING_SOON
    
    # Check if this is the first screening for this movie
    existing_screenings = session.exec(
        select(Screening).where(Screening.movie_id == screening.movie_id)
    ).first()
    is_first_screening = existing_screenings is None
    
    # If it's a COMING_SOON movie and first screening, auto-change to SHOWING
    if was_coming_soon and is_first_screening:
        movie.state = MovieState.SHOWING
        session.add(movie)
    
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
    
    # 🎯 Trigger notifications if this was the first screening for a COMING_SOON movie
    if was_coming_soon and is_first_screening:
        background_tasks.add_task(
            NotificationService.notify_movie_available,
            session,
            screening.movie_id
        )
    
    return db_screening


@router.get("/", response_model=List[ScreeningReadDetailed])
def list_screenings(
    movie_id: Optional[int] = Query(None, description="Filter by movie ID"),
    room_id: Optional[int] = Query(None, description="Filter by room ID"),
    cinema_id: Optional[int] = Query(None, description="Filter by cinema ID"),
    date: Optional[date] = Query(None, description="Filter by date (YYYY-MM-DD)"),
    skip: int = 0,
    limit: int = Query(1000, description="Number of screenings to return"),
    session: Session = Depends(get_session)
):
    """List screenings with optional filters."""
    query = select(Screening).options(
        selectinload(Screening.movie),
        selectinload(Screening.room).selectinload(Room.cinema),
    )
    
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
    
    screenings = session.exec(query.order_by(Screening.screening_time).offset(skip).limit(limit)).all()
    
    # Get unique movie IDs from screenings
    movie_ids = list(set(s.movie_id for s in screenings))
    
    # Load casts for these movies
    if movie_ids:
        cast_statement = select(Cast).where(Cast.movie_id.in_(movie_ids)).order_by(Cast.order)
        all_casts = session.exec(cast_statement).all()
        casts_by_movie = {}
        for cast in all_casts:
            if cast.movie_id not in casts_by_movie:
                casts_by_movie[cast.movie_id] = []
            casts_by_movie[cast.movie_id].append({"name": cast.actor_name, "character": cast.character_name})
        
        # Set cast for each screening's movie
        for screening in screenings:
            screening.movie.cast = casts_by_movie.get(screening.movie_id, [])
    
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
    movie_dict['cast'] = [{"name": cast.actor_name, "character": cast.character_name} for cast in casts]
    
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


@router.put("/{screening_id}", response_model=ScreeningRead)
def update_screening(
    screening_id: int,
    screening_update: ScreeningCreate,
    session: Session = Depends(get_session),
    current_admin: User = Depends(get_current_admin_user)
):
    """Update a screening (admin only)."""
    db_screening = session.get(Screening, screening_id)
    if not db_screening:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Screening with id {screening_id} not found"
        )
    
    # Verify movie exists if changed
    if screening_update.movie_id != db_screening.movie_id:
        movie = session.get(Movie, screening_update.movie_id)
        if not movie:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Movie with id {screening_update.movie_id} not found"
            )
    
    # Verify room exists if changed
    if screening_update.room_id != db_screening.room_id:
        room = session.get(Room, screening_update.room_id)
        if not room:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Room with id {screening_update.room_id} not found"
            )
    
    for key, value in screening_update.model_dump().items():
        setattr(db_screening, key, value)
    
    session.add(db_screening)
    session.commit()
    session.refresh(db_screening)
    return db_screening


@router.delete("/{screening_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_screening(
    screening_id: int,
    session: Session = Depends(get_session),
    current_admin: User = Depends(get_current_admin_user)
):
    """Delete a screening (admin only)."""
    db_screening = session.get(Screening, screening_id)
    if not db_screening:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Screening with id {screening_id} not found"
        )
    
    session.delete(db_screening)
    session.commit()
    return None
