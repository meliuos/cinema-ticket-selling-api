from typing import List, Optional
from sqlmodel import Session, select
from fastapi import HTTPException, status
from datetime import datetime

from app.models.cinema import Cinema, Room, Seat
from app.models.movie import Movie
from app.models.screening import Screening
from app.models.ticket import Ticket
from app.schemas.cinema import SeatBulkCreate
from app.schemas.ticket import TicketCreate


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


def book_tickets(
    session: Session,
    user_id: int,
    screening_id: int,
    seat_ids: List[int]
) -> List[Ticket]:
    """
    Book multiple tickets for a screening.
    
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
    # Verify screening exists
    screening = session.get(Screening, screening_id)
    if not screening:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Screening with id {screening_id} not found"
        )
    
    # Verify screening hasn't already happened
    if screening.screening_time < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot book tickets for past screenings"
        )
    
    # Verify all seats exist and belong to the screening's room
    seats = []
    for seat_id in seat_ids:
        seat = session.get(Seat, seat_id)
        if not seat:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Seat with id {seat_id} not found"
            )
        if seat.room_id != screening.room_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Seat {seat_id} does not belong to the screening's room"
            )
        seats.append(seat)
    
    # Check if any seats are already booked
    existing_tickets_stmt = select(Ticket).where(
        Ticket.screening_id == screening_id,
        Ticket.seat_id.in_(seat_ids),
        Ticket.status == "booked"
    )
    existing_tickets = session.exec(existing_tickets_stmt).all()
    
    if existing_tickets:
        booked_seat_ids = [ticket.seat_id for ticket in existing_tickets]
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Seats {booked_seat_ids} are already booked"
        )
    
    # Create tickets
    tickets = []
    for seat_id in seat_ids:
        ticket = Ticket(
            user_id=user_id,
            screening_id=screening_id,
            seat_id=seat_id,
            price=screening.price,
            status="booked"
        )
        tickets.append(ticket)
        session.add(ticket)
    
    session.commit()
    # Refresh all tickets to get IDs
    for ticket in tickets:
        session.refresh(ticket)
    
    return tickets


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
