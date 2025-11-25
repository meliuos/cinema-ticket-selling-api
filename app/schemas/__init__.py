"""Pydantic schemas for the cinema ticketing system."""

from app.schemas.user import UserCreate, UserRead, UserLogin, Token, TokenData
from app.schemas.cinema import (
    CinemaCreate, CinemaRead,
    RoomCreate, RoomRead,
    SeatCreate, SeatRead, SeatBulkCreate
)
from app.schemas.movie import MovieCreate, MovieRead, MovieUpdate
from app.schemas.screening import ScreeningCreate, ScreeningRead
from app.schemas.ticket import TicketCreate, TicketRead

__all__ = [
    # User
    "UserCreate", "UserRead", "UserLogin", "Token", "TokenData",
    # Cinema
    "CinemaCreate", "CinemaRead",
    "RoomCreate", "RoomRead",
    "SeatCreate", "SeatRead", "SeatBulkCreate",
    # Movie
    "MovieCreate", "MovieRead", "MovieUpdate",
    # Screening
    "ScreeningCreate", "ScreeningRead",
    # Ticket
    "TicketCreate", "TicketRead",
]
