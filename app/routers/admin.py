"""Admin dashboard and analytics routes."""

from fastapi import APIRouter, Depends
from sqlmodel import Session, select, func
from typing import List
from datetime import datetime, timedelta

from app.config import settings
from app.database import get_session
from app.models.user import User
from app.models.cinema import Cinema
from app.models.movie import Movie
from app.models.ticket import Ticket
from app.models.screening import Screening
from app.services.auth import get_current_admin_user

router = APIRouter(prefix=f"{settings.API_V1_PREFIX}/admin", tags=["Admin"])


@router.get("/stats/movies")
async def get_movies_count(
    current_admin: User = Depends(get_current_admin_user),
    session: Session = Depends(get_session)
):
    """Get total movies count."""
    count = session.exec(select(func.count(Movie.id))).first()
    return {"movies_count": count}


@router.get("/stats/cinemas")
async def get_cinemas_count(
    current_admin: User = Depends(get_current_admin_user),
    session: Session = Depends(get_session)
):
    """Get total cinemas count."""
    count = session.exec(select(func.count(Cinema.id))).first()
    return {"cinemas_count": count}


@router.get("/stats/users")
async def get_users_count(
    current_admin: User = Depends(get_current_admin_user),
    session: Session = Depends(get_session)
):
    """Get total users count."""
    count = session.exec(select(func.count(User.id))).first()
    return {"users_count": count}


@router.get("/stats/bookings/recent")
async def get_recent_bookings(
    current_admin: User = Depends(get_current_admin_user),
    session: Session = Depends(get_session),
    days: int = 7,
    limit: int = 10
):
    """Get recent bookings (last N days)."""
    days_ago = datetime.utcnow() - timedelta(days=days)
    recent_bookings = session.exec(
        select(Ticket)
        .where(Ticket.booked_at >= days_ago)
        .order_by(Ticket.booked_at.desc())
        .limit(limit)
    ).all()

    return {
        "recent_bookings": [
            {
                "id": ticket.id,
                "user_id": ticket.user_id,
                "screening_id": ticket.screening_id,
                "seat_id": ticket.seat_id,
                "price": ticket.price,
                "status": ticket.status,
                "booked_at": ticket.booked_at
            }
            for ticket in recent_bookings
        ]
    }


@router.get("/stats/revenue")
async def get_total_revenue(
    current_admin: User = Depends(get_current_admin_user),
    session: Session = Depends(get_session)
):
    """Get total revenue from all tickets."""
    total_revenue = session.exec(select(func.sum(Ticket.price))).first()
    return {"total_revenue": total_revenue or 0}


@router.get("/stats/revenue/period")
async def get_revenue_by_period(
    current_admin: User = Depends(get_current_admin_user),
    session: Session = Depends(get_session),
    days: int = 30
):
    """Get revenue for the last N days."""
    days_ago = datetime.utcnow() - timedelta(days=days)
    revenue = session.exec(
        select(func.sum(Ticket.price))
        .where(Ticket.booked_at >= days_ago)
    ).first()
    return {"revenue_last_period": revenue or 0, "period_days": days}


@router.get("/stats/tickets/total")
async def get_total_tickets_sold(
    current_admin: User = Depends(get_current_admin_user),
    session: Session = Depends(get_session)
):
    """Get total number of tickets sold."""
    total_tickets = session.exec(select(func.count(Ticket.id))).first()
    return {"total_tickets_sold": total_tickets}


@router.get("/stats/movies/popular")
async def get_popular_movies(
    current_admin: User = Depends(get_current_admin_user),
    session: Session = Depends(get_session),
    limit: int = 10
):
    """Get most popular movies by ticket sales."""
    popular_movies = session.exec(
        select(
            Movie.id,
            Movie.title,
            func.count(Ticket.id).label("tickets_sold")
        )
        .join(Screening, Movie.id == Screening.movie_id)
        .join(Ticket, Screening.id == Ticket.screening_id)
        .group_by(Movie.id, Movie.title)
        .order_by(func.count(Ticket.id).desc())
        .limit(limit)
    ).all()

    return {
        "popular_movies": [
            {
                "movie_id": movie.id,
                "title": movie.title,
                "tickets_sold": movie.tickets_sold
            }
            for movie in popular_movies
        ]
    }


@router.get("/stats/today")
async def get_today_stats(
    current_admin: User = Depends(get_current_admin_user),
    session: Session = Depends(get_session)
):
    """Get today's statistics."""
    today = datetime.utcnow().date()
    today_start = datetime.combine(today, datetime.min.time())
    today_end = datetime.combine(today, datetime.max.time())
    
    # Today's bookings count
    today_bookings = session.exec(
        select(func.count(Ticket.id))
        .where(Ticket.booked_at >= today_start)
        .where(Ticket.booked_at <= today_end)
    ).first()
    
    # Today's revenue
    today_revenue = session.exec(
        select(func.sum(Ticket.price))
        .where(Ticket.booked_at >= today_start)
        .where(Ticket.booked_at <= today_end)
    ).first()
    
    return {
        "today_bookings": today_bookings,
        "today_revenue": today_revenue or 0,
        "date": today.isoformat()
    }