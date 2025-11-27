"""Ticket booking routes."""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session, select
from typing import List
from datetime import datetime

from app.config import settings
from app.database import get_session
from app.models.user import User
from app.models.ticket import Ticket
from app.schemas.ticket import TicketCreate, TicketRead, TicketStatusUpdate, TicketConfirmPayment
from app.services.auth import get_current_active_user, get_current_admin_user
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


@router.post("/{ticket_id}/confirm-payment", response_model=TicketRead)
async def confirm_payment(
    ticket_id: int,
    payment_data: TicketConfirmPayment,
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    """Confirm payment for a ticket and update status to confirmed."""
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
            detail="You can only confirm payment for your own tickets"
        )
    
    # Check if ticket is in pending status
    if ticket.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot confirm payment for ticket with status: {ticket.status}"
        )
    
    # Update ticket status to confirmed
    ticket.status = "confirmed"
    ticket.confirmed_at = datetime.utcnow()
    
    session.add(ticket)
    session.commit()
    session.refresh(ticket)
    
    return ticket


@router.get("/", response_model=List[TicketRead])
async def list_all_tickets(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    status_filter: str = Query(None, description="Filter by status: pending, confirmed, cancelled"),
    current_admin: User = Depends(get_current_admin_user),
    session: Session = Depends(get_session)
):
    """List all tickets (admin only endpoint)."""
    query = select(Ticket)
    
    # Apply status filter if provided
    if status_filter:
        query = query.where(Ticket.status == status_filter)
    
    query = query.offset(skip).limit(limit)
    tickets = session.exec(query).all()
    
    return tickets


@router.put("/{ticket_id}/status", response_model=TicketRead)
async def update_ticket_status(
    ticket_id: int,
    status_update: TicketStatusUpdate,
    current_admin: User = Depends(get_current_admin_user),
    session: Session = Depends(get_session)
):
    """Update ticket status (admin only endpoint)."""
    ticket = session.get(Ticket, ticket_id)
    
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ticket with id {ticket_id} not found"
        )
    
    # Validate status
    valid_statuses = ["pending", "confirmed", "cancelled"]
    if status_update.status not in valid_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
        )
    
    # Update status
    ticket.status = status_update.status
    if status_update.status == "confirmed" and not ticket.confirmed_at:
        ticket.confirmed_at = datetime.utcnow()
    
    session.add(ticket)
    session.commit()
    session.refresh(ticket)
    
    return ticket


@router.post("/{ticket_id}/resend", response_model=dict)
async def resend_ticket_confirmation(
    ticket_id: int,
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    """Resend ticket confirmation email (simulated for now)."""
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
            detail="You can only resend confirmation for your own tickets"
        )
    
    # Check if ticket is confirmed
    if ticket.status != "confirmed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can only resend confirmation for confirmed tickets"
        )
    
    # TODO: Implement actual email sending logic
    # For now, just return a success message
    
    return {
        "message": "Ticket confirmation resent successfully",
        "ticket_id": ticket_id,
        "email": current_user.email,
        "sent_at": datetime.utcnow().isoformat()
    }
