"""User-specific routes for search history and recommendations."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select, func
from typing import List
from datetime import datetime, timedelta

from app.config import settings
from app.database import get_session
from app.models.search_history import SearchHistory
from app.models.user import User
from app.models.movie import Movie
from app.models.review import Review
from app.models.ticket import Ticket
from app.schemas.search_history import SearchHistoryRead
from app.schemas.movie import MovieRead
from app.services.auth import get_current_active_user

router = APIRouter(prefix=f"{settings.API_V1_PREFIX}/users/me", tags=["User"])


@router.get("/searches", response_model=List[SearchHistoryRead])
def get_user_search_history(
    limit: int = 20,
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    """Get user's recent search history."""
    searches = session.exec(
        select(SearchHistory)
        .where(SearchHistory.user_id == current_user.id)
        .order_by(SearchHistory.created_at.desc())
        .limit(limit)
    ).all()
    
    return searches


@router.delete("/searches", status_code=status.HTTP_204_NO_CONTENT)
def clear_user_search_history(
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    """Clear all user's search history."""
    searches = session.exec(
        select(SearchHistory).where(SearchHistory.user_id == current_user.id)
    ).all()
    
    for search in searches:
        session.delete(search)
    
    session.commit()
    return None


# Add movie recommendations endpoint
movie_router = APIRouter(prefix=f"{settings.API_V1_PREFIX}/movies", tags=["Movies"])


@movie_router.get("/recommended", response_model=List[MovieRead])
def get_recommended_movies(
    limit: int = 10,
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    """Get recommended movies based on user's viewing history and preferences.
    
    Recommendation logic:
    1. Movies the user has booked tickets for (similar genres)
    2. Highly rated movies (average rating >= 4)
    3. Popular movies (most tickets sold)
    """
    # Get movies user has watched (booked tickets for)
    user_movies = session.exec(
        select(Movie.id)
        .join(Ticket, Ticket.screening_id == Movie.id)
        .where(Ticket.user_id == current_user.id)
        .distinct()
    ).all()
    
    # Get genres from user's watched movies
    user_genres = set()
    if user_movies:
        watched_movies = session.exec(
            select(Movie).where(Movie.id.in_(user_movies))
        ).all()
        for movie in watched_movies:
            if movie.genre:
                user_genres.add(movie.genre.lower())
    
    # Strategy 1: Get highly rated movies in user's preferred genres
    recommended_movies = []
    
    if user_genres:
        # Get movies in preferred genres with high ratings
        for genre in user_genres:
            movies_in_genre = session.exec(
                select(Movie)
                .where(
                    Movie.genre.ilike(f"%{genre}%"),
                    Movie.id.not_in(user_movies) if user_movies else True
                )
                .limit(5)
            ).all()
            recommended_movies.extend(movies_in_genre)
    
    # Strategy 2: Get highly rated movies from reviews
    highly_rated = session.exec(
        select(Movie.id, func.avg(Review.rating).label('avg_rating'))
        .join(Review, Review.movie_id == Movie.id)
        .where(Review.is_deleted == False)
        .group_by(Movie.id)
        .having(func.avg(Review.rating) >= 4.0)
        .order_by(func.avg(Review.rating).desc())
        .limit(5)
    ).all()
    
    if highly_rated:
        movie_ids = [movie_id for movie_id, _ in highly_rated]
        movies = session.exec(
            select(Movie)
            .where(
                Movie.id.in_(movie_ids),
                Movie.id.not_in(user_movies) if user_movies else True
            )
        ).all()
        recommended_movies.extend(movies)
    
    # Strategy 3: Get popular movies (most booked)
    from app.models.screening import Screening
    popular = session.exec(
        select(Movie.id, func.count(Ticket.id).label('ticket_count'))
        .join(Screening, Screening.movie_id == Movie.id)
        .join(Ticket, Ticket.screening_id == Screening.id)
        .where(Movie.id.not_in(user_movies) if user_movies else True)
        .group_by(Movie.id)
        .order_by(func.count(Ticket.id).desc())
        .limit(5)
    ).all()
    
    if popular:
        movie_ids = [movie_id for movie_id, _ in popular]
        movies = session.exec(
            select(Movie).where(Movie.id.in_(movie_ids))
        ).all()
        recommended_movies.extend(movies)
    
    # Remove duplicates and limit
    seen_ids = set()
    unique_movies = []
    for movie in recommended_movies:
        if movie.id not in seen_ids:
            seen_ids.add(movie.id)
            unique_movies.append(movie)
        if len(unique_movies) >= limit:
            break
    
    # If still not enough, add recent movies
    if len(unique_movies) < limit:
        recent = session.exec(
            select(Movie)
            .where(Movie.id.not_in(list(seen_ids)))
            .order_by(Movie.created_at.desc())
            .limit(limit - len(unique_movies))
        ).all()
        unique_movies.extend(recent)
    
    return unique_movies[:limit]
