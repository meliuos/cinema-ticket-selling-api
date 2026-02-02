from typing import List, Optional
from sqlmodel import Session, select, and_
from fastapi import HTTPException, status
from datetime import datetime

from app.models.cinema import Cinema, Room, Seat
from app.models.movie import Movie
from app.models.screening import Screening
from app.models.ticket import Ticket
from app.models.seat_reservation import SeatReservation
from app.schemas.cinema import SeatBulkCreate
from app.schemas.ticket import TicketCreate
from app.services.seat_reservation import SeatReservationService


def bulk_create_seats(session: Session, room_id: int, data: SeatBulkCreate) -> List[Seat]:
    """
    Bulk create seats for a room.
    
    Args:
        session: Database session
        room_id: ID of the room
        data: Bulk creation data (rows, seats_per_row, seat_type)
        
    Returns:
        List of created seats
    """
    # Verify room exists
    room = session.get(Room, room_id)
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Room with id {room_id} not found"
        )
    
    seats = []
    # Always create 7 rows and 10 seats per row
    rows = 7
    seats_per_row = 10
    # Create row labels (A, B, C, ..., Z, AA, AB, ...)
    for row_num in range(rows):
        row_label = chr(65 + row_num) if row_num < 26 else f"{chr(65 + row_num // 26 - 1)}{chr(65 + row_num % 26)}"
        
        for seat_num in range(1, seats_per_row + 1):
            seat = Seat(
                room_id=room_id,
                row_label=row_label,
                seat_number=seat_num,
                seat_type=data.seat_type
            )
            seats.append(seat)
            session.add(seat)
    
    session.commit()
    # Refresh all seats to get IDs
    for seat in seats:
        session.refresh(seat)
    
    return seats


def get_available_seats(session: Session, screening_id: int) -> List[Seat]:
    """
    Get all available (unbooked) seats for a screening.
    
    Args:
        session: Database session
        screening_id: ID of the screening
        
    Returns:
        List of available seats
    """
    # Get the screening
    screening = session.get(Screening, screening_id)
    if not screening:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Screening with id {screening_id} not found"
        )
    
    # Get all seats in the room
    all_seats_stmt = select(Seat).where(Seat.room_id == screening.room_id)
    all_seats = session.exec(all_seats_stmt).all()
    
    # Get booked seat IDs for this screening
    booked_seats_stmt = select(Ticket.seat_id).where(
        Ticket.screening_id == screening_id,
        Ticket.status == "booked"
    )
    booked_seat_ids = set(session.exec(booked_seats_stmt).all())
    
    # Filter out booked seats
    available_seats = [seat for seat in all_seats if seat.id not in booked_seat_ids]
    
    return available_seats


def book_tickets_from_reservation(
    session: Session,
    user_id: int,
    screening_id: int,
    seat_ids: List[int],
    payment_id: str = None
) -> List[Ticket]:
    """
    Book tickets from existing seat reservations.
    
    This function converts active seat reservations into confirmed tickets.
    It should be called after payment confirmation.
    
    IDEMPOTENT: Safe to call multiple times with same payment_id.
    
    Args:
        session: Database session
        user_id: ID of the user booking tickets
        screening_id: ID of the screening
        seat_ids: List of seat IDs to book
        payment_id: Unique payment identifier for idempotency
        
    Returns:
        List of created tickets
        
    Raises:
        HTTPException: If validation fails or reservations don't exist
    """
    # IDEMPOTENCY CHECK: If payment_id provided, check if already processed
    if payment_id:
        existing_tickets = session.exec(
            select(Ticket).where(
                and_(
                    Ticket.screening_id == screening_id,
                    Ticket.seat_id.in_(seat_ids),
                    Ticket.user_id == user_id,
                    Ticket.status == "confirmed"
                )
            )
        ).all()
        
        if existing_tickets and len(existing_tickets) == len(seat_ids):
            # Payment already processed - return existing tickets 
            return existing_tickets
    
    # Lock seat rows first 
    locked_seats = session.exec(
        select(Seat).where(Seat.id.in_(seat_ids)).with_for_update()
    ).all()
    
    if len(locked_seats) != len(seat_ids):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Some seats could not be locked"
        )
    # Verify the user has active reservations for these seats
    reservations = session.exec(
        select(SeatReservation).where(
            and_(
                SeatReservation.screening_id == screening_id,
                SeatReservation.seat_id.in_(seat_ids),
                SeatReservation.user_id == user_id,
                SeatReservation.status == "active",
                SeatReservation.expires_at > datetime.utcnow()
            )
        ).with_for_update()  # Also lock reservations
    ).all()
    
    if len(reservations) != len(seat_ids):
        missing_seats = set(seat_ids) - {res.seat_id for res in reservations}
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"No valid reservations found for seats: {list(missing_seats)}"
        )
    
    # Get screening for price
    screening = session.get(Screening, screening_id)
    if not screening:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Screening with id {screening_id} not found"
        )
    
    # Create tickets and update reservation status
    tickets = []
    try:
        for reservation in reservations:
            # Create ticket
            ticket = Ticket(
                user_id=user_id,
                screening_id=screening_id,
                seat_id=reservation.seat_id,
                price=screening.price,
                status="confirmed",
                confirmed_at=datetime.utcnow(),
                payment_id=payment_id  # For idempotency tracking
            )
            tickets.append(ticket)
            session.add(ticket)
            
            # Mark reservation as booked
            reservation.status = "booked"
            session.add(reservation)
        
        session.commit()
        
        # Refresh tickets to get IDs
        for ticket in tickets:
            session.refresh(ticket)
        
        # Broadcast seat booking updates
        try:
            from app.services.websocket_manager import manager
            import asyncio
            
            # Prepare seat updates for broadcasting
            seat_updates = []
            for ticket in tickets:
                seat_updates.append({
                    "seat_id": ticket.seat_id,
                    "status": "booked",
                    "booked_by": user_id
                })
            
            # Broadcast updates
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    asyncio.create_task(
                        manager.broadcast_multiple_seat_updates(screening_id, seat_updates)
                    )
                else:
                    asyncio.run(
                        manager.broadcast_multiple_seat_updates(screening_id, seat_updates)
                    )
            except Exception as broadcast_error:
                import logging
                logging.warning(f"Failed to broadcast ticket bookings: {broadcast_error}")
                
        except ImportError:
            pass
        
        return tickets
        
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to book tickets from reservations"
        )


def book_tickets(
    session: Session,
    user_id: int,
    screening_id: int,
    seat_ids: List[int]
) -> List[Ticket]:
    """
    Book tickets with proper concurrency handling through reservations.
    
    This function first reserves the seats, then immediately converts them
    to confirmed tickets. This ensures atomic operation and prevents race conditions.
    
    Args:
        session: Database session
        user_id: ID of the user booking tickets
        screening_id: ID of the screening
        seat_ids: List of seat IDs to book
        
    Returns:
        List of created tickets
        
    Raises:
        HTTPException: If validation fails
    """
    # First, try to reserve the seats
    try:
        reservations = SeatReservationService.reserve_seats(
            session=session,
            user_id=user_id,
            screening_id=screening_id,
            seat_ids=seat_ids
        )
    except HTTPException:
        # Re-raise reservation errors
        raise
    
    # If reservations successful, immediately convert to bookings
    try:
        tickets = book_tickets_from_reservation(
            session=session,
            user_id=user_id,
            screening_id=screening_id,
            seat_ids=seat_ids
        )
        return tickets
        
    except HTTPException:
        # If booking fails, cancel the reservations
        SeatReservationService.cancel_reservations(
            session=session,
            user_id=user_id,
            screening_id=screening_id,
            seat_ids=seat_ids
        )
        raise


def cancel_ticket(session: Session, ticket_id: int, user_id: int) -> Ticket:
    """
    Cancel a ticket.
    
    Args:
        session: Database session
        ticket_id: ID of the ticket to cancel
        user_id: ID of the user (for authorization)
        
    Returns:
        Cancelled ticket
        
    Raises:
        HTTPException: If ticket not found or user unauthorized
    """
    ticket = session.get(Ticket, ticket_id)
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ticket with id {ticket_id} not found"
        )
    
    # Verify ticket belongs to user
    if ticket.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only cancel your own tickets"
        )
    
    # Verify ticket not already cancelled
    if ticket.status == "cancelled":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ticket is already cancelled"
        )
    
    # Update ticket status
    ticket.status = "cancelled"
    session.add(ticket)
    session.commit()
    session.refresh(ticket)
    
    return ticket
