"""Screening routes."""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session, select
from typing import List, Optional

from app.config import settings
from app.database import get_session
from app.models.movie import Movie
from app.models.cinema import Room, Seat
from app.models.screening import Screening
from app.schemas.screening import ScreeningCreate, ScreeningRead
from app.schemas.cinema import SeatRead
from app.services.cinema import get_available_seats

router = APIRouter(prefix=f"{settings.API_V1_PREFIX}/screenings", tags=["Screenings"])


@router.post(
    "/",
    response_model=ScreeningRead,
    status_code=status.HTTP_201_CREATED
)
def create_screening(screening: ScreeningCreate, session: Session = Depends(get_session)):
    """Create a new screening (showtime)."""
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


@router.get("/", response_model=List[ScreeningRead])
def list_screenings(
    movie_id: Optional[int] = Query(None, description="Filter by movie ID"),
    room_id: Optional[int] = Query(None, description="Filter by room ID"),
    cinema_id: Optional[int] = Query(None, description="Filter by cinema ID"),
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
    
    screenings = session.exec(query.offset(skip).limit(limit)).all()
    return screenings


@router.get("/{screening_id}", response_model=ScreeningRead)
def get_screening(screening_id: int, session: Session = Depends(get_session)):
    """Get a specific screening by ID."""
    screening = session.get(Screening, screening_id)
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
