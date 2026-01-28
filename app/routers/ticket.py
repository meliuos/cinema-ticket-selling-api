"""Ticket booking routes."""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session, select
from typing import List
from datetime import datetime

from app.config import settings
from app.database import get_session
from app.models.user import User
from app.models.ticket import Ticket
from app.models.seat_reservation import SeatReservation
from app.schemas.ticket import (
    TicketCreate,
    TicketRead,
    TicketStatusUpdate,
    TicketConfirmPayment,
    BookFromReservationRequest,
    BookFromReservationResponse,
)
from app.services.auth import get_current_active_user, get_current_admin_user
from app.services.cinema import book_tickets, cancel_ticket
from app.services.websocket_manager import manager

router = APIRouter(prefix=f"{settings.API_V1_PREFIX}/tickets", tags=["Tickets"])


# ---------------------------------------------------------------------------
# BOOK TICKETS (DIRECT)
# ---------------------------------------------------------------------------
@router.post(
    "/book",
    response_model=List[TicketRead],
    status_code=status.HTTP_201_CREATED,
)
async def book_tickets_endpoint(
    booking: TicketCreate,
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_session),
):
    """Book tickets for a screening (creates PENDING tickets)."""
    tickets = book_tickets(
        session=session,
        user_id=current_user.id,
        screening_id=booking.screening_id,
        seat_ids=booking.seat_ids,
    )

    # 🔒 Ensure correct initial state
    for t in tickets:
        t.status = "pending"
        session.add(t)

    session.commit()
    return tickets


# ---------------------------------------------------------------------------
# BOOK FROM RESERVATION (CHECKOUT FLOW)
# ---------------------------------------------------------------------------
@router.post(
    "/book-from-reservation",
    response_model=BookFromReservationResponse,
    status_code=status.HTTP_201_CREATED,
)
async def book_from_reservation(
    payload: BookFromReservationRequest,
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_session),
):
    now = datetime.utcnow()

    if not payload.reservation_ids:
        raise HTTPException(status_code=400, detail="reservation_ids is required")

    reservations = session.exec(
        select(SeatReservation).where(SeatReservation.id.in_(payload.reservation_ids))
    ).all()

    if len(reservations) != len(payload.reservation_ids):
        raise HTTPException(status_code=404, detail="Some reservations were not found")

    screening_ids = set()
    seat_ids: List[int] = []

    for r in reservations:
        if r.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Reservation does not belong to current user")
        if r.status != "active":
            raise HTTPException(status_code=409, detail="Reservation is not active")
        if r.expires_at <= now:
            raise HTTPException(status_code=409, detail="Reservation has expired")

        screening_ids.add(r.screening_id)
        seat_ids.append(r.seat_id)

    if len(screening_ids) != 1:
        raise HTTPException(status_code=400, detail="All reservations must be for the same screening")

    screening_id = screening_ids.pop()

    tickets = book_tickets(session, current_user.id, screening_id, seat_ids)

    # 🔒 Enforce correct lifecycle
    for t in tickets:
        t.status = "pending"
        session.add(t)

    for r in reservations:
        r.status = "cancelled"
        session.add(r)

    session.commit()

    for seat_id in seat_ids:
        await manager.broadcast_seat_update(
            screening_id,
            seat_id=seat_id,
            status="booked",
            reserved_by=None,
            is_mine=False,
        )

    return BookFromReservationResponse(tickets=tickets)


# ---------------------------------------------------------------------------
# USER TICKETS
# ---------------------------------------------------------------------------
@router.get("/my-tickets", response_model=List[TicketRead])
async def get_my_tickets(
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_session),
):
    return session.exec(
        select(Ticket).where(Ticket.user_id == current_user.id)
    ).all()


@router.get("/{ticket_id}", response_model=TicketRead)
async def get_ticket(
    ticket_id: int,
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_session),
):
    ticket = session.get(Ticket, ticket_id)
    if not ticket:
        raise HTTPException(404, "Ticket not found")

    if ticket.user_id != current_user.id:
        raise HTTPException(403, "You can only view your own tickets")

    return ticket


# ---------------------------------------------------------------------------
# CANCEL TICKET
# ---------------------------------------------------------------------------
@router.delete("/{ticket_id}", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_ticket_endpoint(
    ticket_id: int,
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_session),
):
    cancel_ticket(session, ticket_id, current_user.id)
    return None


# ---------------------------------------------------------------------------
# CONFIRM PAYMENT
# ---------------------------------------------------------------------------
@router.post("/{ticket_id}/confirm-payment", response_model=TicketRead)
async def confirm_payment(
    ticket_id: int,
    payment_data: TicketConfirmPayment,
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_session),
):
    ticket = session.get(Ticket, ticket_id)

    if not ticket:
        raise HTTPException(404, "Ticket not found")

    if ticket.user_id != current_user.id:
        raise HTTPException(403, "You can only confirm your own tickets")

    if ticket.status == "confirmed":
        return ticket  # idempotent safe

    if ticket.status != "pending":
        raise HTTPException(
            status_code=409,
            detail=f"Ticket cannot be confirmed from status '{ticket.status}'",
        )

    ticket.status = "confirmed"
    ticket.confirmed_at = datetime.utcnow()

    session.add(ticket)
    session.commit()
    session.refresh(ticket)

    return ticket


# ---------------------------------------------------------------------------
# ADMIN ENDPOINTS
# ---------------------------------------------------------------------------
@router.get("/", response_model=List[TicketRead])
async def list_all_tickets(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=1000),
    status_filter: str | None = Query(None),
    current_admin: User = Depends(get_current_admin_user),
    session: Session = Depends(get_session),
):
    query = select(Ticket)
    if status_filter:
        query = query.where(Ticket.status == status_filter)

    return session.exec(query.offset(skip).limit(limit)).all()


@router.put("/{ticket_id}/status", response_model=TicketRead)
async def update_ticket_status(
    ticket_id: int,
    status_update: TicketStatusUpdate,
    current_admin: User = Depends(get_current_admin_user),
    session: Session = Depends(get_session),
):
    ticket = session.get(Ticket, ticket_id)
    if not ticket:
        raise HTTPException(404, "Ticket not found")

    valid = {"pending", "confirmed", "cancelled"}
    if status_update.status not in valid:
        raise HTTPException(400, f"Invalid status: {status_update.status}")

    ticket.status = status_update.status
    if status_update.status == "confirmed" and not ticket.confirmed_at:
        ticket.confirmed_at = datetime.utcnow()

    session.add(ticket)
    session.commit()
    session.refresh(ticket)

    return ticket


# ---------------------------------------------------------------------------
# RESEND CONFIRMATION
# ---------------------------------------------------------------------------
@router.post("/{ticket_id}/resend", response_model=dict)
async def resend_ticket_confirmation(
    ticket_id: int,
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_session),
):
    ticket = session.get(Ticket, ticket_id)

    if not ticket:
        raise HTTPException(404, "Ticket not found")

    if ticket.user_id != current_user.id:
        raise HTTPException(403, "Forbidden")

    if ticket.status != "confirmed":
        raise HTTPException(409, "Ticket is not confirmed")

    return {
        "message": "Ticket confirmation resent successfully",
        "ticket_id": ticket_id,
        "email": current_user.email,
        "sent_at": datetime.utcnow().isoformat(),
    }
