"""Ticket booking routes."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List

from app.config import settings
from app.database import get_session
from app.models.user import User
from app.models.ticket import Ticket
from app.schemas.ticket import TicketCreate, TicketRead
from app.services.auth import get_current_active_user
from app.services.cinema import book_tickets, cancel_ticket

router = APIRouter(prefix=f"{settings.API_V1_PREFIX}/tickets", tags=["Tickets"])


@router.post(
    "/book",
    response_model=List[TicketRead],
    status_code=status.HTTP_201_CREATED
)
async def book_tickets_endpoint(
    booking: TicketCreate,
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    """Book tickets for a screening (requires authentication)."""
    tickets = book_tickets(
        session=session,
        user_id=current_user.id,
        screening_id=booking.screening_id,
        seat_ids=booking.seat_ids
    )
    return tickets


@router.get("/my-tickets", response_model=List[TicketRead])
async def get_my_tickets(
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    """Get current user's tickets."""
    tickets = session.exec(
        select(Ticket).where(Ticket.user_id == current_user.id)
    ).all()
    return tickets


@router.get("/{ticket_id}", response_model=TicketRead)
async def get_ticket(
    ticket_id: int,
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    """Get a specific ticket by ID."""
    ticket = session.get(Ticket, ticket_id)
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ticket with id {ticket_id} not found"
        )
    
    # Verify ticket belongs to user
    if ticket.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view your own tickets"
        )
    
    return ticket


@router.delete("/{ticket_id}", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_ticket_endpoint(
    ticket_id: int,
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    """Cancel a ticket."""
    cancel_ticket(session, ticket_id, current_user.id)
    return None
