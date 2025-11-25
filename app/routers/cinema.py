"""Cinema and Room routes."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List

from app.config import settings
from app.database import get_session
from app.models.cinema import Cinema, Room
from app.schemas.cinema import CinemaCreate, CinemaRead, RoomCreate, RoomRead

router = APIRouter(prefix=settings.API_V1_PREFIX, tags=["Cinemas", "Rooms"])


# ============================================================================
# Cinema Endpoints
# ============================================================================

@router.post(
    "/cinemas/",
    response_model=CinemaRead,
    status_code=status.HTTP_201_CREATED,
    tags=["Cinemas"]
)
def create_cinema(cinema: CinemaCreate, session: Session = Depends(get_session)):
    """Create a new cinema."""
    db_cinema = Cinema.model_validate(cinema)
    session.add(db_cinema)
    session.commit()
    session.refresh(db_cinema)
    return db_cinema


@router.get("/cinemas/", response_model=List[CinemaRead], tags=["Cinemas"])
def list_cinemas(
    skip: int = 0,
    limit: int = 100,
    session: Session = Depends(get_session)
):
    """List all cinemas."""
    cinemas = session.exec(select(Cinema).offset(skip).limit(limit)).all()
    return cinemas


@router.get("/cinemas/{cinema_id}", response_model=CinemaRead, tags=["Cinemas"])
def get_cinema(cinema_id: int, session: Session = Depends(get_session)):
    """Get a specific cinema by ID."""
    cinema = session.get(Cinema, cinema_id)
    if not cinema:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cinema with id {cinema_id} not found"
        )
    return cinema


# ============================================================================
# Room Endpoints
# ============================================================================

@router.post(
    "/cinemas/{cinema_id}/rooms/",
    response_model=RoomRead,
    status_code=status.HTTP_201_CREATED,
    tags=["Rooms"]
)
def create_room(
    cinema_id: int,
    room: RoomCreate,
    session: Session = Depends(get_session)
):
    """Create a new room in a cinema."""
    # Verify cinema exists
    cinema = session.get(Cinema, cinema_id)
    if not cinema:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cinema with id {cinema_id} not found"
        )
    
    db_room = Room(**room.model_dump(), cinema_id=cinema_id)
    session.add(db_room)
    session.commit()
    session.refresh(db_room)
    return db_room


@router.get(
    "/cinemas/{cinema_id}/rooms/",
    response_model=List[RoomRead],
    tags=["Rooms"]
)
def list_cinema_rooms(
    cinema_id: int,
    session: Session = Depends(get_session)
):
    """List all rooms in a cinema."""
    rooms = session.exec(select(Room).where(Room.cinema_id == cinema_id)).all()
    return rooms


@router.get("/rooms/{room_id}", response_model=RoomRead, tags=["Rooms"])
def get_room(room_id: int, session: Session = Depends(get_session)):
    """Get a specific room by ID."""
    room = session.get(Room, room_id)
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Room with id {room_id} not found"
        )
    return room
