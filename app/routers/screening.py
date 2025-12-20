"""Screening routes."""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session, select
from sqlalchemy.orm import selectinload
from typing import List, Optional
from datetime import datetime, date

from app.config import settings
from app.database import get_session
from app.models.movie import Movie
from app.models.cinema import Room, Seat
from app.models.screening import Screening
from app.models.user import User
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


@router.get("/", response_model=List[ScreeningReadDetailed])
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
    
    screenings = session.exec(query.offset(skip).limit(limit)).all()
    return screenings


@router.get("/{screening_id}", response_model=ScreeningRead)
def get_screening(screening_id: int, session: Session = Depends(get_session)):
    """Get a specific screening by ID."""
    screening = session.exec(
        select(Screening)
        .options(
            selectinload(Screening.movie),
            selectinload(Screening.room).selectinload(Room.cinema),
        )
        .where(Screening.id == screening_id)
    ).first()
    if not screening:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Screening with id {screening_id} not found"
        )
    return screening


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
