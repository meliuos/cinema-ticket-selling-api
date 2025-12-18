"""Movie routes."""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session, select, or_
from typing import List, Optional
from datetime import datetime, date

from app.config import settings
from app.database import get_session
from app.models.movie import Movie
from app.models.screening import Screening
from app.models.user import User
from app.models.cast import Cast
from app.schemas.movie import MovieCreate, MovieRead, MovieUpdate
from app.schemas.screening import ScreeningRead
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
    session: Session = Depends(get_session)
):
    """List all movies."""
    movies = session.exec(select(Movie).offset(skip).limit(limit)).all()
    # Normalize genre fields for backward compatibility
    return [MovieRead(**normalize_movie_genre(movie)) for movie in movies]


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
    # Normalize genre fields for backward compatibility
    return [MovieRead(**normalize_movie_genre(movie)) for movie in movies]


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
    # Normalize genre fields for backward compatibility
    return [MovieRead(**normalize_movie_genre(movie)) for movie in movies]


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
    # Normalize genre fields for backward compatibility
    return [MovieRead(**normalize_movie_genre(movie)) for movie in movies]


@router.get("/{movie_id}", response_model=MovieRead)
def get_movie(movie_id: int, session: Session = Depends(get_session)):
    """Get a specific movie by ID."""
    movie = session.get(Movie, movie_id)
    if not movie:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Movie with id {movie_id} not found"
        )
    return normalize_movie_genre(movie)


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


@router.get("/{movie_id}/showtimes", response_model=List[ScreeningRead])
def get_movie_showtimes(
    movie_id: int,
    date: Optional[date] = Query(None, description="Filter by date (YYYY-MM-DD)"),
    skip: int = 0,
    limit: int = 100,
    session: Session = Depends(get_session)
):
    """Get all showtimes for a specific movie, optionally filtered by date."""
    # Check if movie exists
    movie = session.get(Movie, movie_id)
    if not movie:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Movie with id {movie_id} not found"
        )
    
    # Build query
    query = select(Screening).where(Screening.movie_id == movie_id)
    
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
    
    session.delete(movie)
    session.commit()
    return None
