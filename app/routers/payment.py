"""Payment processing routes with fake payment simulation."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select, SQLModel
from typing import List, Optional
from datetime import datetime
import random
import uuid

from app.config import settings
from app.database import get_session
from app.models.user import User
from app.models.ticket import Ticket
from app.models.seat_reservation import SeatReservation
from app.schemas.ticket import TicketRead
from app.services.auth import get_current_active_user
from app.services.cinema import book_tickets_from_reservation

router = APIRouter(prefix=f"{settings.API_V1_PREFIX}/payment", tags=["Payment"])


class PaymentRequest(SQLModel):
    """Payment request schema."""
    screening_id: int
    seat_ids: List[int]
    payment_method: str = "credit_card"  


class PaymentResponse(SQLModel):
    """Payment response schema."""
    success: bool
    payment_id: Optional[str] = None
    transaction_id: Optional[str] = None
    message: str
    tickets: Optional[List[TicketRead]] = None
    amount: float


class PaymentHistoryItem(SQLModel):
    """Payment history item schema."""
    id: int
    screening_id: int
    seat_id: int
    price: float
    status: str
    booked_at: datetime
    confirmed_at: Optional[datetime] = None
    payment_id: Optional[str] = None
    # Additional details (can be populated from joins)
    movie_title: Optional[str] = None
    cinema_name: Optional[str] = None
    showtime: Optional[datetime] = None
    seat_info: Optional[str] = None


@router.post("/process", response_model=PaymentResponse)
async def process_payment(
    payment_request: PaymentRequest,
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    """
    Process payment for seat reservations.
    
    Fake payment simulation:
    - 95% success rate
    - 5% failure rate (random failures to simulate real-world scenarios)
    
    On success:
    - Converts seat reservations to confirmed tickets
    - Returns payment confirmation with tickets
    
    On failure:
    - Returns error message
    - Reservations remain active (will expire after 5 minutes)
    """
    # Verify all seats are reserved by the current user
    reservations = session.exec(
        select(SeatReservation).where(
            SeatReservation.screening_id == payment_request.screening_id,
            SeatReservation.user_id == current_user.id,
            SeatReservation.status == "active",
            SeatReservation.seat_id.in_(payment_request.seat_ids)
        )
    ).all()
    
    if len(reservations) != len(payment_request.seat_ids):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Some seats are not reserved by you or have expired. Please reserve them again."
        )
    
    # Check if reservations have expired
    current_time = datetime.utcnow()
    for reservation in reservations:
        if reservation.expires_at < current_time:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Your seat reservations have expired. Please reserve them again."
            )
    
    #Calculate total amount
    total_amount = sum(r.seat.seat_type == "vip" and 15.0 or 10.0 for r in reservations)
    
    # Simulate payment processing (95% success, 5% failure)
    payment_successful = random.random() < 0.95
    
    if not payment_successful:
        # Payment failed - return error
        return PaymentResponse(
            success=False,
            message="Payment failed. Please check your payment method and try again.",
            amount=total_amount
        )
    
    #  Payment successful - generate IDs
    payment_id = f"PAY-{uuid.uuid4().hex[:16].upper()}"
    transaction_id = f"TXN-{uuid.uuid4().hex[:12].upper()}"
    
    # Convert reservations to confirmed tickets
    try:
        tickets = book_tickets_from_reservation(
            session=session,
            user_id=current_user.id,
            screening_id=payment_request.screening_id,
            seat_ids=payment_request.seat_ids,
            payment_id=payment_id
        )
        
        return PaymentResponse(
            success=True,
            payment_id=payment_id,
            transaction_id=transaction_id,
            message=f"Payment successful! {len(tickets)} ticket(s) confirmed.",
            tickets=tickets,
            amount=total_amount
        )
        
    except Exception as e:
        # If booking fails, rollback and return error
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Payment was processed but ticket booking failed: {str(e)}"
        )


@router.get("/history", response_model=List[TicketRead])
async def get_payment_history(
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    """
    Get payment history - all tickets purchased by the current user.
    
    Returns tickets ordered by booking date (most recent first).
    Only includes confirmed and pending tickets (not cancelled).
    """
    tickets = session.exec(
        select(Ticket)
        .where(Ticket.user_id == current_user.id)
        .where(Ticket.status.in_(["confirmed", "pending"]))
        .order_by(Ticket.booked_at.desc())
    ).all()
    
    return tickets


@router.get("/history/all", response_model=List[TicketRead])
async def get_all_payment_history(
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    """
    Get complete payment history - all tickets including cancelled ones.
    
    Returns all tickets ordered by booking date (most recent first).
    """
    tickets = session.exec(
        select(Ticket)
        .where(Ticket.user_id == current_user.id)
        .order_by(Ticket.booked_at.desc())
    ).all()
    
    return tickets


@router.get("/ticket/{payment_id}", response_model=List[TicketRead])
async def get_tickets_by_payment_id(
    payment_id: str,
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    """
    Get all tickets associated with a specific payment ID.
    
    Useful for viewing all tickets from a single transaction.
    """
    tickets = session.exec(
        select(Ticket)
        .where(Ticket.payment_id == payment_id)
        .where(Ticket.user_id == current_user.id)
    ).all()
    
    if not tickets:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No tickets found for payment ID: {payment_id}"
        )
    
    return tickets
