"""Movie routes."""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session, select, delete, or_
from sqlalchemy.orm import selectinload
from typing import List, Optional
from datetime import datetime, date

from app.config import settings
from app.database import get_session
from app.models.movie import Movie, MovieState
from app.models.screening import Screening
from app.models.cinema import Room
from app.models.user import User
from app.models.cast import Cast
from app.models.ticket import Ticket
from app.models.seat_reservation import SeatReservation
from app.models.favorite import Favorite
from app.models.review import Review, ReviewReactionModel
from app.schemas.movie import MovieCreate, MovieRead, MovieUpdate
from app.schemas.screening import ScreeningReadDetailed
from app.schemas.cast import CastRead
from app.services.auth import get_current_admin_user

def normalize_movie_genre(movie: Movie) -> dict:
    """Normalize movie data, converting genre string to list if needed."""
    movie_dict = movie.model_dump()
    if isinstance(movie_dict.get('genre'), str):
        movie_dict['genre'] = [movie_dict['genre']] if movie_dict['genre'] else None
    return movie_dict

router = APIRouter(prefix=f"{settings.API_V1_PREFIX}/movies", tags=["Movies"])


@router.post(
    "/",
    response_model=MovieRead,
    status_code=status.HTTP_201_CREATED
)
def create_movie(
    movie: MovieCreate,
    session: Session = Depends(get_session),
    current_admin: User = Depends(get_current_admin_user)
):
    """Create a new movie with comprehensive details (admin only)."""
    db_movie = Movie.model_validate(movie)
    session.add(db_movie)
    session.commit()
    session.refresh(db_movie)
    return normalize_movie_genre(db_movie)


@router.get("/", response_model=List[MovieRead])
def list_movies(
    skip: int = 0,
    limit: int = 100,
    state: Optional[MovieState] = Query(None, description="Filter by movie state (SHOWING, COMING_SOON, ENDED)"),
    sort_by: Optional[str] = Query(None, description="Sort by: 'trending' (ticket sales), 'release_date', or default (created_at)"),
    include_ended: bool = Query(False, description="Include movies that have ended (ignored if state is specified)"),
    session: Session = Depends(get_session)
):
    """
    List all movies with cast details. 
    
    - Filter by state: ?state=SHOWING or ?state=COMING_SOON or ?state=ENDED
    - Sort by trending: ?sort_by=trending (most sold tickets first)
    - Sort by release date: ?sort_by=release_date
    - Combine: ?state=SHOWING&sort_by=trending for trending movies currently showing
    """
    from sqlalchemy import func
    
    # Handle trending sort separately (requires joins)
    if sort_by == "trending":
        trending_movies = session.exec(
            select(Movie, func.count(Ticket.id).label('ticket_count'))
            .join(Screening, Movie.id == Screening.movie_id)
            .join(Ticket, Screening.id == Ticket.screening_id)
            .where(
                Ticket.status.in_(["confirmed", "booked"]),
                Movie.state == (state if state else MovieState.SHOWING)
            )
            .group_by(Movie.id)
            .order_by(func.count(Ticket.id).desc())
            .offset(skip)
            .limit(limit)
        ).all()
        
        result = []
        for movie, ticket_count in trending_movies:
            statement = select(Cast).where(Cast.movie_id == movie.id).order_by(Cast.order)
            casts = session.exec(statement).all()
            movie_dict = normalize_movie_genre(movie)
            movie_dict['cast'] = [cast.actor_name for cast in casts]
            result.append(movie_dict)
        
        return result
    
    # Standard query
    query = select(Movie)
    
    # Apply state filter
    if state:
        query = query.where(Movie.state == state)
    elif not include_ended:
        query = query.where(Movie.state != MovieState.ENDED)
    
    # Apply sorting
    if sort_by == "release_date":
        query = query.order_by(Movie.release_date.asc())
    else:
        query = query.order_by(Movie.created_at.desc())
    
    movies = session.exec(query.offset(skip).limit(limit)).all()
    
    result = []
    for movie in movies:
        # Get cast details for this movie
        statement = select(Cast).where(Cast.movie_id == movie.id).order_by(Cast.order)
        casts = session.exec(statement).all()
        
        # Normalize movie and add cast
        movie_dict = normalize_movie_genre(movie)
        movie_dict['cast'] = [cast.actor_name for cast in casts]
        result.append(movie_dict)
    
    return result


@router.get("/coming-soon", response_model=List[MovieRead])
def list_coming_soon_movies(
    skip: int = 0,
    limit: int = 100,
    session: Session = Depends(get_session)
):
    """List movies that are coming soon (state = COMING_SOON)."""
    movies = session.exec(
        select(Movie)
        .where(Movie.state == MovieState.COMING_SOON)
        .order_by(Movie.release_date.asc())
        .offset(skip)
        .limit(limit)
    ).all()
    
    result = []
    for movie in movies:
        # Get cast details for this movie
        statement = select(Cast).where(Cast.movie_id == movie.id).order_by(Cast.order)
        casts = session.exec(statement).all()
        
        # Normalize movie and add cast
        movie_dict = normalize_movie_genre(movie)
        movie_dict['cast'] = [cast.actor_name for cast in casts]
        result.append(movie_dict)
    
    return result


@router.get("/trending", response_model=List[MovieRead])
def list_trending_movies(
    skip: int = 0,
    limit: int = 50,
    session: Session = Depends(get_session)
):
    """List trending movies based on ticket sales (most sold tickets first)."""
    from sqlalchemy import func
    
    # Get movies ordered by ticket sales count (only showing movies)
    trending_movies = session.exec(
        select(Movie, func.count(Ticket.id).label('ticket_count'))
        .join(Screening, Movie.id == Screening.movie_id)
        .join(Ticket, Screening.id == Ticket.screening_id)
        .where(
            Ticket.status.in_(["confirmed", "booked"]),  # Only count sold tickets
            Movie.state == MovieState.SHOWING  
        )
        .group_by(Movie.id)
        .order_by(func.count(Ticket.id).desc())
        .offset(skip)
        .limit(limit)
    ).all()
    
    result = []
    for movie, ticket_count in trending_movies:
        # Get cast details for this movie
        statement = select(Cast).where(Cast.movie_id == movie.id).order_by(Cast.order)
        casts = session.exec(statement).all()
        
        # Normalize movie and add cast
        movie_dict = normalize_movie_genre(movie)
        movie_dict['cast'] = [cast.actor_name for cast in casts]
        result.append(movie_dict)
    
    return result


@router.get("/search", response_model=List[MovieRead])
def search_movies(
    q: str = Query(..., min_length=1, description="Search query for movie title, genre, cast, or director"),
    skip: int = 0,
    limit: int = 100,
    session: Session = Depends(get_session)
):
    """Search movies by title, genre, cast, or director."""
    search_term = f"%{q.lower()}%"

    # Search across multiple fields
    statement = select(Movie).where(
        or_(
            Movie.title.ilike(search_term),
            Movie.genre.ilike(search_term),
            Movie.director.ilike(search_term),
            Movie.description.ilike(search_term)
        )
    ).offset(skip).limit(limit)

    movies = session.exec(statement).all()
    
    result = []
    for movie in movies:
        # Get cast details for this movie
        cast_statement = select(Cast).where(Cast.movie_id == movie.id).order_by(Cast.order)
        casts = session.exec(cast_statement).all()
        
        # Normalize movie and add cast
        movie_dict = normalize_movie_genre(movie)
        movie_dict['cast'] = [cast.actor_name for cast in casts]
        result.append(movie_dict)
    
    return result


@router.get("/filter", response_model=List[MovieRead])
def filter_movies(
    genre: Optional[str] = Query(None, description="Filter by genre"),
    rating: Optional[str] = Query(None, description="Filter by rating (e.g., PG, PG-13, R)"),
    min_rating: Optional[float] = Query(None, ge=0, le=10, description="Minimum rating (0-10)"),
    release_year: Optional[int] = Query(None, description="Filter by release year"),
    director: Optional[str] = Query(None, description="Filter by director"),
    country: Optional[str] = Query(None, description="Filter by country"),
    language: Optional[str] = Query(None, description="Filter by language"),
    skip: int = 0,
    limit: int = 100,
    session: Session = Depends(get_session)
):
    """Filter movies by various criteria."""
    query = select(Movie)

    # Apply filters
    if genre:
        query = query.where(Movie.genre.ilike(f"%{genre}%"))

    if rating:
        query = query.where(Movie.rating == rating)

    if min_rating is not None:
        # Note: This assumes we might add a numeric rating field later
        # For now, we'll filter by rating string presence
        pass

    if release_year:
        query = query.where(Movie.release_date >= date(release_year, 1, 1)).where(
            Movie.release_date < date(release_year + 1, 1, 1)
        )

    if director:
        query = query.where(Movie.director.ilike(f"%{director}%"))

    if country:
        query = query.where(Movie.country.ilike(f"%{country}%"))

    if language:
        query = query.where(Movie.language.ilike(f"%{language}%"))

    # Order by release date (newest first)
    query = query.order_by(Movie.release_date.desc())

    movies = session.exec(query.offset(skip).limit(limit)).all()
    
    result = []
    for movie in movies:
        # Get cast details for this movie
        cast_statement = select(Cast).where(Cast.movie_id == movie.id).order_by(Cast.order)
        casts = session.exec(cast_statement).all()
        
        # Normalize movie and add cast
        movie_dict = normalize_movie_genre(movie)
        movie_dict['cast'] = [cast.actor_name for cast in casts]
        result.append(movie_dict)
    
    return result


@router.get("/advanced-search", response_model=List[MovieRead])
def advanced_search_movies(
    title: Optional[str] = Query(None, description="Search in movie title"),
    genre: Optional[str] = Query(None, description="Search in movie genre"),
    director: Optional[str] = Query(None, description="Search in director name"),
    cast: Optional[str] = Query(None, description="Search in cast names"),
    description: Optional[str] = Query(None, description="Search in movie description"),
    rating: Optional[str] = Query(None, description="Filter by rating"),
    release_year_from: Optional[int] = Query(None, description="Release year from"),
    release_year_to: Optional[int] = Query(None, description="Release year to"),
    country: Optional[str] = Query(None, description="Filter by country"),
    language: Optional[str] = Query(None, description="Filter by language"),
    sort_by: str = Query("release_date", description="Sort by: title, release_date, rating"),
    sort_order: str = Query("desc", description="Sort order: asc or desc"),
    skip: int = 0,
    limit: int = 100,
    session: Session = Depends(get_session)
):
    """Advanced search with multiple filters and sorting options."""
    query = select(Movie)

    # Apply search filters
    if title:
        query = query.where(Movie.title.ilike(f"%{title}%"))

    if genre:
        query = query.where(Movie.genre.ilike(f"%{genre}%"))

    if director:
        query = query.where(Movie.director.ilike(f"%{director}%"))

    if cast:
        # Join with Cast table to search in cast names
        query = query.join(Cast, Movie.id == Cast.movie_id).where(Cast.actor_name.ilike(f"%{cast}%")).distinct()

    if description:
        query = query.where(Movie.description.ilike(f"%{description}%"))

    if rating:
        query = query.where(Movie.rating == rating)

    if release_year_from:
        query = query.where(Movie.release_date >= date(release_year_from, 1, 1))

    if release_year_to:
        query = query.where(Movie.release_date < date(release_year_to + 1, 1, 1))

    if country:
        query = query.where(Movie.country.ilike(f"%{country}%"))

    if language:
        query = query.where(Movie.language.ilike(f"%{language}%"))

    # Apply sorting
    if sort_by == "title":
        if sort_order == "asc":
            query = query.order_by(Movie.title.asc())
        else:
            query = query.order_by(Movie.title.desc())
    elif sort_by == "release_date":
        if sort_order == "asc":
            query = query.order_by(Movie.release_date.asc())
        else:
            query = query.order_by(Movie.release_date.desc())
    elif sort_by == "rating":
        # For now, sort by title as fallback since we don't have numeric rating
        if sort_order == "asc":
            query = query.order_by(Movie.title.asc())
        else:
            query = query.order_by(Movie.title.desc())
    else:
        # Default sorting
        query = query.order_by(Movie.release_date.desc())

    movies = session.exec(query.offset(skip).limit(limit)).all()
    
    result = []
    for movie in movies:
        # Get cast details for this movie
        cast_statement = select(Cast).where(Cast.movie_id == movie.id).order_by(Cast.order)
        casts = session.exec(cast_statement).all()
        
        # Normalize movie and add cast
        movie_dict = normalize_movie_genre(movie)
        movie_dict['cast'] = [cast.actor_name for cast in casts]
        result.append(movie_dict)
    
    return result


@router.get("/{movie_id}", response_model=MovieRead)
def get_movie(movie_id: int, session: Session = Depends(get_session)):
    """Get a specific movie by ID with cast details."""
    movie = session.get(Movie, movie_id)
    if not movie:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Movie with id {movie_id} not found"
        )
    
    # Get cast details
    statement = select(Cast).where(Cast.movie_id == movie_id).order_by(Cast.order)
    casts = session.exec(statement).all()
    
    # Convert movie to dict and add cast details
    movie_dict = normalize_movie_genre(movie)
    movie_dict['cast'] = [cast.actor_name for cast in casts]
    
    return movie_dict


@router.get("/{movie_id}/cast", response_model=List[CastRead])
def get_movie_cast(movie_id: int, session: Session = Depends(get_session)):
    """Get the cast list for a specific movie."""
    movie = session.get(Movie, movie_id)
    if not movie:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Movie with id {movie_id} not found"
        )
    statement = select(Cast).where(Cast.movie_id == movie_id).order_by(Cast.order)
    casts = session.exec(statement).all()
    return casts


@router.get("/{movie_id}/showtimes", response_model=List[ScreeningReadDetailed])
def get_movie_showtimes(
    movie_id: int,
    date: Optional[date] = Query(None, description="Filter by date (YYYY-MM-DD)"),
    skip: int = 0,
    limit: int = 100,
    session: Session = Depends(get_session)
):
    """Get all future showtimes for a specific movie, optionally filtered by date."""
    # Check if movie exists
    movie = session.get(Movie, movie_id)
    if not movie:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Movie with id {movie_id} not found"
        )
    
    # Build query with relationships loaded, only future screenings
    now = datetime.utcnow()
    query = select(Screening).where(
        Screening.movie_id == movie_id,
        Screening.screening_time > now
    ).options(
        selectinload(Screening.room).selectinload(Room.cinema)
    )
    
    if date:
        # Filter by date
        start_of_day = datetime.combine(date, datetime.min.time())
        end_of_day = datetime.combine(date, datetime.max.time())
        query = query.where(
            Screening.screening_time >= start_of_day,
            Screening.screening_time <= end_of_day
        )
    
    # Order by screening time
    query = query.order_by(Screening.screening_time)
    
    screenings = session.exec(query.offset(skip).limit(limit)).all()
    return screenings


@router.patch("/{movie_id}", response_model=MovieRead)
def update_movie(
    movie_id: int,
    movie_update: MovieUpdate,
    session: Session = Depends(get_session),
    current_admin: User = Depends(get_current_admin_user)
):
    """Update a movie's information (admin only)."""
    db_movie = session.get(Movie, movie_id)
    if not db_movie:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Movie with id {movie_id} not found"
        )
    
    # Update only provided fields
    movie_data = movie_update.model_dump(exclude_unset=True)
    
    # Validate state transitions if state is being updated
    if 'state' in movie_data and movie_data['state'] != db_movie.state:
        state_order = {MovieState.COMING_SOON: 0, MovieState.SHOWING: 1, MovieState.ENDED: 2}
        if state_order[movie_data['state']] < state_order[db_movie.state]:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid state transition: Cannot change from {db_movie.state} to {movie_data['state']}"
            )
    
    for key, value in movie_data.items():
        setattr(db_movie, key, value)
    
    db_movie.updated_at = datetime.utcnow()
    session.add(db_movie)
    session.commit()
    session.refresh(db_movie)
    return normalize_movie_genre(db_movie)


@router.delete("/{movie_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_movie(
    movie_id: int,
    session: Session = Depends(get_session),
    current_admin: User = Depends(get_current_admin_user)
):
    """Delete a movie (admin only)."""
    movie = session.get(Movie, movie_id)
    if not movie:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Movie with id {movie_id} not found"
        )
    
    # Delete all associated data in correct 
    # 1. Delete review reactions for reviews of this movie
    session.exec(delete(ReviewReactionModel).where(ReviewReactionModel.review_id.in_(
        select(Review.id).where(Review.movie_id == movie_id)
    )))
    
    # 2. Delete reviews for this movie
    session.exec(delete(Review).where(Review.movie_id == movie_id))
    
    # 3. Delete favorites for this movie
    session.exec(delete(Favorite).where(Favorite.movie_id == movie_id))
    
    # 4. Delete cast for this movie
    session.exec(delete(Cast).where(Cast.movie_id == movie_id))
    
    # 5. Delete seat reservations for screenings of this movie
    session.exec(delete(SeatReservation).where(SeatReservation.screening_id.in_(
        select(Screening.id).where(Screening.movie_id == movie_id)
    )))
    
    # 6. Delete tickets for screenings of this movie
    session.exec(delete(Ticket).where(Ticket.screening_id.in_(
        select(Screening.id).where(Screening.movie_id == movie_id)
    )))
    
    # 7. Delete screenings for this movie
    session.exec(delete(Screening).where(Screening.movie_id == movie_id))
    
    # 8. Finally delete the movie
    session.delete(movie)
    session.commit()
    return None
