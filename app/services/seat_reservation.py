"""
Seat reservation service with proper concurrency handling.

This service implements database-level locking to prevent race conditions
when multiple users try to reserve the same seat simultaneously.
"""

from typing import List, Optional, Tuple
from datetime import datetime, timedelta
from sqlmodel import Session, select, and_, or_
from fastapi import HTTPException, status
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload
import logging

logger = logging.getLogger(__name__)

from app.models.cinema import Seat
from app.models.screening import Screening
from app.models.ticket import Ticket
from app.models.seat_reservation import SeatReservation
from app.models.user import User
from app.models.movie import Movie, MovieState
from app.schemas.seat_reservation import SeatAvailabilityRead


class SeatReservationService:
    """Service for handling seat reservations with concurrency control."""
    
    RESERVATION_DURATION_MINUTES = 5
    
    @staticmethod
    def cleanup_expired_reservations(session: Session) -> Tuple[int, dict]:
        """
        Clean up expired seat reservations.
        
        Args:
            session: Database session
            
        Returns:
            Tuple of (count of expired reservations, seat_updates dict)
        """
        from app.services.websocket_manager import manager
        
        current_time = datetime.utcnow()
        
        # Find expired active reservations
        expired_reservations = session.exec(
            select(SeatReservation).where(
                and_(
                    SeatReservation.status == "active",
                    SeatReservation.expires_at < current_time
                )
            )
        ).all()
        
        # Update their status and collect for broadcasting
        count = 0
        seat_updates = {}  
        
        for reservation in expired_reservations:
            reservation.status = "expired"
            session.add(reservation)
            count += 1
            
            # Prepare broadcast data
            screening_id = reservation.screening_id
            if screening_id not in seat_updates:
                seat_updates[screening_id] = []
            
            seat_updates[screening_id].append({
                "seat_id": reservation.seat_id,
                "status": "available",
                "previously_reserved_by": reservation.user_id
            })
                
        return count, seat_updates if count > 0 else {}
    
    @staticmethod
    def get_seat_availability(
        session: Session, 
        screening_id: int, 
        current_user_id: int = None
    ) -> List[SeatAvailabilityRead]:
        """
        Get availability status for all seats in a screening.
        
        Args:
            session: Database session
            screening_id: ID of the screening
            current_user_id: Optional ID of the current user to mark their reservations
            
        Returns:
            List of seat availability information with is_mine flag
        """
        # Clean up expired reservations 
        SeatReservationService.cleanup_expired_reservations(session)
        
        # Get the screening and its room
        screening = session.get(Screening, screening_id)
        if not screening:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Screening with id {screening_id} not found"
            )
        
        # Get all seats in the room
        seats = session.exec(
            select(Seat).where(Seat.room_id == screening.room_id)
            .order_by(Seat.row_label, Seat.seat_number)
        ).all()
        
        # Get booked tickets for this screening
        booked_tickets = session.exec(
            select(Ticket).where(
                and_(
                    Ticket.screening_id == screening_id,
                    Ticket.status.in_(["confirmed", "booked"])
                )
            )
        ).all()
        booked_seat_ids = {ticket.seat_id for ticket in booked_tickets}
        
        # Get active reservations for this screening
        active_reservations = session.exec(
            select(SeatReservation).where(
                and_(
                    SeatReservation.screening_id == screening_id,
                    SeatReservation.status == "active",
                    SeatReservation.expires_at > datetime.utcnow()
                )
            )
        ).all()
        reservation_map = {res.seat_id: res for res in active_reservations}
        
        # Build availability list
        availability_list = []
        for seat in seats:
            if seat.id in booked_seat_ids:
                seat_status = "booked"
                reserved_by = None
                expires_at = None
                is_mine = False
            elif seat.id in reservation_map:
                reservation = reservation_map[seat.id]
                reserved_by = reservation.user_id
                expires_at = reservation.expires_at
                # Check if this is the current user's reservation
                is_mine = current_user_id is not None and reservation.user_id == current_user_id
                # Use different status for user's own reservations
                seat_status = "reserved_by_me" if is_mine else "reserved"
            else:
                seat_status = "available"
                reserved_by = None
                expires_at = None
                is_mine = False
            
            availability_list.append(
                SeatAvailabilityRead(
                    seat=seat,
                    status=seat_status,
                    reserved_by=reserved_by,
                    is_mine=is_mine,
                    expires_at=expires_at
                )
            )
        
        return availability_list
    
    @staticmethod
    def reserve_seats(
        session: Session, 
        user_id: int, 
        screening_id: int, 
        seat_ids: List[int]
    ) -> Tuple[List[SeatReservation], dict]:
        """
        Reserve seats for a user with proper concurrency handling.
        
        This method uses database-level locking (FOR UPDATE) to prevent
        race conditions when multiple users try to reserve the same seats.
        
        Args:
            session: Database session
            user_id: ID of the user reserving seats
            screening_id: ID of the screening
            seat_ids: List of seat IDs to reserve
            
        Returns:
            Tuple of (List of created seat reservations, dict of broadcast updates)
            
        Raises:
            HTTPException: If validation fails or seats cannot be reserved
        """
        logger.info(f"[RESERVE] Starting seat reservation for user {user_id}, screening {screening_id}, seats {seat_ids}")
        logger.info(f"[RESERVE] Session state before cleanup: in_transaction={session.in_transaction()}, is_active={session.is_active}")
        
        # Clean up expired reservations first
        cleanup_count, cleanup_updates = SeatReservationService.cleanup_expired_reservations(session)
        logger.info(f"[RESERVE] After cleanup: count={cleanup_count}, session state: in_transaction={session.in_transaction()}")
        
        # Flush cleanup changes to ensure they're visible in this transaction
        if cleanup_count > 0:
            session.flush()
        
        # Validate screening exists and is future
        screening = session.get(Screening, screening_id)
        if not screening:
            logger.error(f"[RESERVE] Screening {screening_id} not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Screening with id {screening_id} not found"
            )
        
        # Get movie to check state
        movie = session.get(Movie, screening.movie_id)
        if movie and movie.state == MovieState.COMING_SOON:
            logger.error(f"[RESERVE] Cannot reserve seats for coming soon movie: {movie.title}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot book seats for coming soon movies"
            )
        
        if screening.screening_time < datetime.utcnow():
            logger.error(f"[RESERVE] Screening {screening_id} is in the past: {screening.screening_time}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot reserve seats for past screenings"
            )
        
        # Validate seats exist and belong to the screening's room
        seats = []
        for seat_id in seat_ids:
            seat = session.get(Seat, seat_id)
            if not seat:
                logger.error(f"[RESERVE] Seat {seat_id} not found")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Seat with id {seat_id} not found"
                )
            if seat.room_id != screening.room_id:
                logger.error(f"[RESERVE] Seat {seat_id} (room {seat.room_id}) doesn't belong to screening room {screening.room_id}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Seat {seat_id} does not belong to the screening's room"
                )
            seats.append(seat)
        
        # Start transaction with row locking
        try:
            logger.info(f"[RESERVE] About to lock seats. Session state: in_transaction={session.in_transaction()}")
            # Lock seats for update to prevent concurrent reservations
            locked_seats = session.exec(
                select(Seat).where(Seat.id.in_(seat_ids)).with_for_update()
            ).all()
            
            if len(locked_seats) != len(seat_ids):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Some seats could not be locked"
                )
            
            # Check for existing bookings 
            existing_bookings = session.exec(
                select(Ticket).where(
                    and_(
                        Ticket.screening_id == screening_id,
                        Ticket.seat_id.in_(seat_ids),
                        Ticket.status.in_(["confirmed", "booked"])
                    )
                )
            ).all()
            
            if existing_bookings:
                booked_seat_ids = [ticket.seat_id for ticket in existing_bookings]
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Seats {booked_seat_ids} are already booked"
                )
            
            # Check for active reservations by other users
            active_reservations = session.exec(
                select(SeatReservation).where(
                    and_(
                        SeatReservation.screening_id == screening_id,
                        SeatReservation.seat_id.in_(seat_ids),
                        SeatReservation.status == "active",
                        SeatReservation.expires_at > datetime.utcnow(),
                        SeatReservation.user_id != user_id  
                    )
                )
            ).all()
            
            if active_reservations:
                reserved_seat_ids = [res.seat_id for res in active_reservations]
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Seats {reserved_seat_ids} are currently reserved by other users"
                )
            
            # Cancel any existing reservations by the same user for these seats
            existing_user_reservations = session.exec(
                select(SeatReservation).where(
                    and_(
                        SeatReservation.screening_id == screening_id,
                        SeatReservation.seat_id.in_(seat_ids),
                        SeatReservation.user_id == user_id,
                        SeatReservation.status == "active"
                    )
                )
            ).all()
            
            for reservation in existing_user_reservations:
                reservation.status = "cancelled"
                session.add(reservation)
            
            # Create new reservations
            current_time = datetime.utcnow()
            expires_at = current_time + timedelta(minutes=SeatReservationService.RESERVATION_DURATION_MINUTES)
            
            reservations = []
            for seat_id in seat_ids:
                reservation = SeatReservation(
                    screening_id=screening_id,
                    seat_id=seat_id,
                    user_id=user_id,
                    reserved_at=current_time,
                    expires_at=expires_at,
                    status="active"
                )
                reservations.append(reservation)
                session.add(reservation)
            
            # Flush to get IDs and commit the transaction
            session.flush()
            session.commit()
            
            reservation_ids = [r.id for r in reservations]
            stmt = (
                select(SeatReservation)
                .options(joinedload(SeatReservation.seat), joinedload(SeatReservation.user))
                .where(SeatReservation.id.in_(reservation_ids))
            )
            reservations = list(session.exec(stmt).unique())
            
            # Collect data for broadcasting
            seat_updates_for_broadcast = []
            for reservation in reservations:
                seat_updates_for_broadcast.append({
                    "seat_id": reservation.seat_id,
                    "status": "reserved",
                    "reserved_by": user_id,
                    "expires_at": reservation.expires_at.isoformat()
                })
            
            all_updates = {}
            
            # Add cleanup updates 
            for screening_id_key, updates in cleanup_updates.items():
                all_updates[screening_id_key] = updates.copy()
            
            # Add new reservation updates
            if screening_id not in all_updates:
                all_updates[screening_id] = []
            
            all_updates[screening_id].extend(seat_updates_for_broadcast)
            
            logger.info(f"[RESERVE] About to return. Session state: in_transaction={session.in_transaction()}, is_active={session.is_active}")
            logger.info(f"[RESERVE] Reservation IDs: {[r.id for r in reservations]}")
            return reservations, all_updates
            
        except IntegrityError as e:
            logger.error(f"[RESERVE] IntegrityError occurred: {e}. Rolling back.")
            session.rollback()
            logger.info(f"[RESERVE] After rollback in IntegrityError. Session state: in_transaction={session.in_transaction()}")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Seats are no longer available due to concurrent booking"
            )
        except Exception as e:
            logger.error(f"[RESERVE] Exception occurred: {type(e).__name__}: {e}. Rolling back.")
            session.rollback()
            logger.info(f"[RESERVE] After rollback in Exception. Session state: in_transaction={session.in_transaction()}")
            raise
    
    @staticmethod
    def extend_reservation(
        session: Session, 
        user_id: int, 
        screening_id: int,
        seat_ids: List[int],
        additional_minutes: int = 5
    ) -> Tuple[List[SeatReservation], dict]:
        """
        Extend existing seat reservations for a user.
        
        EDGE CASE SAFE: Validates reservation ownership, expiry, and status.
        
        Args:
            session: Database session
            user_id: ID of the user
            screening_id: ID of the screening
            seat_ids: List of seat IDs to extend
            additional_minutes: Additional minutes to extend
            
        Returns:
            Tuple of (List of extended reservations, dict of broadcast updates)
        """
        current_time = datetime.utcnow()
        
        # Lock seat rows first
        locked_seats = session.exec(
            select(Seat).where(Seat.id.in_(seat_ids)).with_for_update()
        ).all()
        
        if len(locked_seats) != len(seat_ids):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Some seats could not be locked"
            )
        
        # Find reservations with STRICT validation
        reservations = session.exec(
            select(SeatReservation).where(
                and_(
                    SeatReservation.screening_id == screening_id,
                    SeatReservation.seat_id.in_(seat_ids),
                    SeatReservation.user_id == user_id,  
                    SeatReservation.status == "active",  
                    SeatReservation.expires_at > current_time
                )
            ).with_for_update()  
        ).all()
        
        if len(reservations) != len(seat_ids):
            missing_count = len(seat_ids) - len(reservations)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot extend: {missing_count} reservations are invalid, expired, or don't belong to you"
            )
        
        # Double-check none are already booked 
        booked_reservations = [r for r in reservations if r.status == "booked"]
        if booked_reservations:
            booked_seat_ids = [r.seat_id for r in booked_reservations]
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Cannot extend: seats {booked_seat_ids} are already booked"
            )
        
        # Extend expiration time
        extension = timedelta(minutes=additional_minutes)
        for reservation in reservations:
            reservation.expires_at += extension
            session.add(reservation)
        
        session.commit()
        
        # Prepare broadcast updates
        seat_updates = []
        for reservation in reservations:
            seat_updates.append({
                "seat_id": reservation.seat_id,
                "status": "reserved",
                "reserved_by": user_id,
                "expires_at": reservation.expires_at.isoformat(),
                "extended": True
            })
        
        broadcast_updates = {screening_id: seat_updates}
        return reservations, broadcast_updates
    
    @staticmethod
    def cancel_reservations(
        session: Session, 
        user_id: int, 
        screening_id: int,
        seat_ids: Optional[List[int]] = None
    ) -> Tuple[int, dict]:
        """
        Cancel seat reservations for a user.
        
        Args:
            session: Database session
            user_id: ID of the user
            screening_id: ID of the screening
            seat_ids: Specific seat IDs to cancel (if None, cancels all user's reservations)
            
        Returns:
            Tuple of (Number of reservations cancelled, dict of broadcast updates)
        """
        query = select(SeatReservation).where(
            and_(
                SeatReservation.screening_id == screening_id,
                SeatReservation.user_id == user_id,
                SeatReservation.status == "active"
            )
        )
        
        if seat_ids:
            query = query.where(SeatReservation.seat_id.in_(seat_ids))
        
        reservations = session.exec(query).all()
        
        # Collect seat updates for broadcasting
        seat_updates = []
        count = 0
        for reservation in reservations:
            reservation.status = "cancelled"
            session.add(reservation)
            count += 1
            
            # Prepare broadcast data
            seat_updates.append({
                "seat_id": reservation.seat_id,
                "status": "available",
                "previously_reserved_by": reservation.user_id
            })
        
        broadcast_updates = {}
        if count > 0:
            session.commit()
            broadcast_updates = {screening_id: seat_updates}
        
        return count, broadcast_updates
    
    @staticmethod
    def get_user_reservations(
        session: Session, 
        user_id: int,
        include_expired: bool = False,
        screening_id: int = None
    ) -> List[SeatReservation]:
        """
        Get all reservations for a user.
        
        Args:
            session: Database session
            user_id: ID of the user
            include_expired: Whether to include expired reservations
            screening_id: Optional filter by screening
            
        Returns:
            List of user's reservations
        """
        query = select(SeatReservation).where(SeatReservation.user_id == user_id)
        
        if screening_id:
            query = query.where(SeatReservation.screening_id == screening_id)
        
        if not include_expired:
            # Only include active reservations that haven't expired
            query = query.where(
                and_(
                    SeatReservation.status == "active",
                    SeatReservation.expires_at > datetime.utcnow()
                )
            )
        
        reservations = session.exec(
            query.order_by(SeatReservation.reserved_at.desc())
        ).all()
        
        return reservations