"""Cinema and Room routes."""

from collections import defaultdict
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session, select, or_
from typing import List, Optional
from datetime import datetime, date

from app.config import settings
from app.database import get_session
from app.models.cinema import Cinema, Room
from app.models.screening import Screening
from app.models.movie import Movie
from app.models.user import User
from app.schemas.cinema import CinemaCreate, CinemaRead, CinemaUpdate, CinemaListResponse, RoomCreate, RoomRead
from app.schemas.movie import MovieRead, MovieListResponse
from app.routers.movie import normalize_movie_genre
from app.schemas.screening import (
    MovieShowtimesRead,
)
from app.services.auth import get_current_admin_user

router = APIRouter(prefix=settings.API_V1_PREFIX, tags=["Cinemas", "Rooms"])


# ============================================================================
# Cinema Endpoints
# ============================================================================


@router.post(
    "/cinemas/",
    response_model=CinemaRead,
    status_code=status.HTTP_201_CREATED,
    tags=["Cinemas"],
)
def create_cinema(
    cinema: CinemaCreate,
    current_admin: User = Depends(get_current_admin_user),
    session: Session = Depends(get_session),
):
    """Create a new cinema (admin only)."""
    db_cinema = Cinema.model_validate(cinema)
    session.add(db_cinema)
    session.commit()
    session.refresh(db_cinema)
    return db_cinema


@router.get("/cinemas/", response_model=CinemaListResponse, tags=["Cinemas"])
def list_cinemas(
    skip: int = 0, limit: int = 100, session: Session = Depends(get_session)
):
    """List all cinemas with total count."""
    # Get total count
    total = session.exec(select(Cinema)).all()
    total_count = len(total)
    
    # Get paginated cinemas
    cinemas = session.exec(select(Cinema).offset(skip).limit(limit)).all()
    
    return CinemaListResponse(cinemas=list(cinemas), total=total_count)


@router.get("/cinemas/search", response_model=List[CinemaRead], tags=["Cinemas"])
def search_cinemas(
    q: str = Query(
        ..., min_length=1, description="Search query for cinema name, city, or address"
    ),
    session: Session = Depends(get_session),
):
    """Search cinemas by name, city, or address."""
    search_term = f"%{q}%"
    cinemas = session.exec(
        select(Cinema).where(
            or_(
                Cinema.name.ilike(search_term),
                Cinema.city.ilike(search_term),
                Cinema.address.ilike(search_term),
            )
        )
    ).all()
    return cinemas


@router.get("/cinemas/{cinema_id}", response_model=CinemaRead, tags=["Cinemas"])
def get_cinema(cinema_id: int, session: Session = Depends(get_session)):
    """Get a specific cinema by ID."""
    cinema = session.get(Cinema, cinema_id)
    if not cinema:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cinema with id {cinema_id} not found",
        )
    return cinema


@router.patch("/cinemas/{cinema_id}", response_model=CinemaRead, tags=["Cinemas"])
def update_cinema(
    cinema_id: int,
    cinema_update: CinemaUpdate,
    current_admin: User = Depends(get_current_admin_user),
    session: Session = Depends(get_session),
):
    """Update a cinema (admin only)."""
    cinema = session.get(Cinema, cinema_id)
    if not cinema:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cinema with id {cinema_id} not found",
        )
    
    # Update only provided fields
    update_data = cinema_update.model_dump(exclude_unset=True)
    cinema.sqlmodel_update(update_data)
    session.add(cinema)
    session.commit()
    session.refresh(cinema)
    return cinema


@router.delete("/cinemas/{cinema_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Cinemas"])
def delete_cinema(
    cinema_id: int,
    current_admin: User = Depends(get_current_admin_user),
    session: Session = Depends(get_session),
):
    """Delete a cinema (admin only)."""
    cinema = session.get(Cinema, cinema_id)
    if not cinema:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cinema with id {cinema_id} not found",
        )
    
    session.delete(cinema)
    session.commit()
    return None


@router.get(
    "/cinemas/{cinema_id}/amenities", response_model=List[str], tags=["Cinemas"]
)
def get_cinema_amenities(cinema_id: int, session: Session = Depends(get_session)):
    """Get list of amenities for a specific cinema."""
    cinema = session.get(Cinema, cinema_id)
    if not cinema:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cinema with id {cinema_id} not found",
        )
    return cinema.amenities or []


@router.get(
    "/cinemas/{cinema_id}/movies", response_model=MovieListResponse, tags=["Cinemas"]
)
def get_cinema_movies(
    cinema_id: int,
    skip: int = 0,
    limit: int = 100,
    session: Session = Depends(get_session)
):
    """Get all movies currently showing at a specific cinema."""
    # Verify cinema exists
    cinema = session.get(Cinema, cinema_id)
    if not cinema:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cinema with id {cinema_id} not found",
        )

    # Get all rooms for this cinema
    rooms = session.exec(select(Room).where(Room.cinema_id == cinema_id)).all()
    room_ids = [room.id for room in rooms]

    if not room_ids:
        return MovieListResponse(movies=[], total=0)

    # Get unique movie IDs from screenings in these rooms
    movie_ids = session.exec(
        select(Screening.movie_id).where(Screening.room_id.in_(room_ids)).distinct()
    ).all()

    if not movie_ids:
        return MovieListResponse(movies=[], total=0)
    # Get total count of unique movies
    total = len(movie_ids)

    # Get the actual movies with pagination
    movies = session.exec(
        select(Movie).where(Movie.id.in_(movie_ids)).offset(skip).limit(limit)
    ).all()

    return MovieListResponse(
        movies=[MovieRead(**normalize_movie_genre(movie)) for movie in movies],
        total=total
    )


@router.get(
    "/cinemas/{cinema_id}/showtimes",
    response_model=list[MovieShowtimesRead],
    tags=["Cinemas"],
)
def get_grouped_cinema_showtimes(
    cinema_id: int,
    date: Optional[date] = Query(None),
    session: Session = Depends(get_session),
):
    query = select(Screening).join(Room).join(Movie).where(Room.cinema_id == cinema_id)
    if date:
        start = datetime.combine(date, datetime.min.time())
        end = datetime.combine(date, datetime.max.time())
        query = query.where(
            Screening.screening_time >= start, Screening.screening_time <= end
        )
    screenings = session.exec(query).all()
    grouped = defaultdict(lambda: {
        "movie": None,
        "price": None,
        "showtimes": []
    })
    for s in screenings:
        movie_id = s.movie.id

        grouped[movie_id]["movie"] = s.movie
        grouped[movie_id]["price"] = s.price
        grouped[movie_id]["showtimes"].append({
            "id": s.id,
            "screening_time": s.screening_time
        })
    return list(grouped.values())


# ============================================================================
# Room Endpoints
# ============================================================================


@router.post(
    "/cinemas/{cinema_id}/rooms/",
    response_model=RoomRead,
    status_code=status.HTTP_201_CREATED,
    tags=["Rooms"],
)
def create_room(
    cinema_id: int,
    room: RoomCreate,
    current_admin: User = Depends(get_current_admin_user),
    session: Session = Depends(get_session),
):
    """Create a new room in a cinema (admin only)."""
    # Verify cinema exists
    cinema = session.get(Cinema, cinema_id)
    if not cinema:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cinema with id {cinema_id} not found",
        )

    db_room = Room(**room.model_dump(), cinema_id=cinema_id)
    session.add(db_room)
    session.commit()
    session.refresh(db_room)
    return db_room


@router.get(
    "/cinemas/{cinema_id}/rooms/", response_model=List[RoomRead], tags=["Rooms"]
)
def list_cinema_rooms(cinema_id: int, session: Session = Depends(get_session)):
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
            detail=f"Room with id {room_id} not found",
        )
    return room
