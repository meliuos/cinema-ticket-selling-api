"""Showtime routes - convenience endpoints for screenings."""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session, select
from typing import List, Optional
from datetime import datetime, date

from app.config import settings
from app.database import get_session
from app.models.movie import Movie
from app.models.cinema import Cinema, Room
from app.models.screening import Screening
from app.schemas.screening import ScreeningRead
from app.schemas.cinema import SeatRead
from app.services.cinema import get_available_seats

router = APIRouter(prefix=f"{settings.API_V1_PREFIX}/showtimes", tags=["Showtimes"])


@router.get("/", response_model=List[ScreeningRead])
def list_showtimes(
    date: Optional[date] = Query(None, description="Filter by date (YYYY-MM-DD)"),
    movie_id: Optional[int] = Query(None, description="Filter by movie ID"),
    cinema_id: Optional[int] = Query(None, description="Filter by cinema ID"),
    skip: int = 0,
    limit: int = 100,
    session: Session = Depends(get_session)
):
    """List all showtimes with optional filters (alias for screenings)."""
    query = select(Screening)
    
    if movie_id:
        query = query.where(Screening.movie_id == movie_id)
    
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


@router.get("/{showtime_id}", response_model=ScreeningRead)
def get_showtime(showtime_id: int, session: Session = Depends(get_session)):
    """Get a specific showtime by ID (alias for screening)."""
    screening = session.get(Screening, showtime_id)
    if not screening:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Showtime with id {showtime_id} not found"
        )
    return screening


@router.get("/{showtime_id}/seats", response_model=List[SeatRead])
def get_showtime_seats(showtime_id: int, session: Session = Depends(get_session)):
    """Get available seats for a showtime (alias for screening)."""
    screening = session.get(Screening, showtime_id)
    if not screening:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Showtime with id {showtime_id} not found"
        )
    available_seats = get_available_seats(session, showtime_id)
    return available_seats
