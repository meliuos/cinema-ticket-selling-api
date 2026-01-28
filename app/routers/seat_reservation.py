"""Seat reservation routes with concurrency handling."""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlmodel import Session
from typing import List
from datetime import datetime

from app.config import settings
from app.database import get_session
from app.models.user import User
from app.schemas.seat_reservation import (
    SeatReservationCreate,
    SeatReservationRead,
    SeatReservationResponse,
    SeatAvailabilityRead
)
from app.services.auth import get_current_active_user
from app.services.seat_reservation import SeatReservationService

router = APIRouter(prefix=f"{settings.API_V1_PREFIX}/seat-reservations", tags=["Seat Reservations"])


async def broadcast_seat_updates(broadcast_updates: dict):
    """Background task to broadcast seat updates via WebSocket."""
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        from app.services.websocket_manager import manager
        
        if not broadcast_updates:
            return
        
        for screening_id, updates in broadcast_updates.items():
            await manager.broadcast_multiple_seat_updates(screening_id, updates)
            
    except Exception as e:
        logger.error(f"[BROADCAST] Failed to broadcast seat updates: {e}", exc_info=True)


@router.get("/screening/{screening_id}/availability", response_model=List[SeatAvailabilityRead])
def get_seat_availability(
    screening_id: int,
    session: Session = Depends(get_session)
):
    """
    Get seat availability for a screening (anonymous/public).
    
    Returns all seats with their current status:
    - available: Seat can be reserved
    - reserved: Seat is temporarily held by a user
    - booked: Seat is permanently booked
    
    Note: Use /screening/{screening_id}/availability/me for user-aware availability
    that distinguishes your own reservations.
    """
    availability = SeatReservationService.get_seat_availability(session, screening_id)
    return availability


@router.get("/screening/{screening_id}/availability/me", response_model=List[SeatAvailabilityRead])
def get_seat_availability_for_user(
    screening_id: int,
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    """
    Get seat availability for a screening with user context.
    
    Returns all seats with their current status and marks the current user's reservations:
    - available: Seat can be reserved
    - reserved: Seat is temporarily held by ANOTHER user
    - reserved_by_me: Seat is temporarily held by the CURRENT user
    - booked: Seat is permanently booked
    
    The `is_mine` field is True for seats reserved by the current user.
    """
    availability = SeatReservationService.get_seat_availability(
        session, 
        screening_id, 
        current_user_id=current_user.id
    )
    return availability


@router.post("/reserve", response_model=SeatReservationResponse)
def reserve_seats(
    reservation_request: SeatReservationCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    """
    Reserve seats for a user.
    
    This endpoint uses database-level locking to prevent race conditions
    when multiple users try to reserve the same seats simultaneously.
    
    Seats are held for 5 minutes by default.
    """
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        seat_ids = reservation_request.get_seat_ids()
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    reservations, broadcast_updates = SeatReservationService.reserve_seats(
        session=session,
        user_id=current_user.id,
        screening_id=reservation_request.screening_id,
        seat_ids=seat_ids
    )
    
    # Schedule WebSocket broadcast as background task
    if broadcast_updates:
        background_tasks.add_task(broadcast_seat_updates, broadcast_updates)
    
    return SeatReservationResponse(
        reservations=reservations,
        expires_in_minutes=SeatReservationService.RESERVATION_DURATION_MINUTES,
        message=f"Reserved {len(reservations)} seats for {SeatReservationService.RESERVATION_DURATION_MINUTES} minutes"
    )


@router.post("/toggle", status_code=status.HTTP_200_OK)
def toggle_seat_reservation(
    reservation_request: SeatReservationCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    """
    Toggle seat reservation - reserve if available, unreserve if already reserved by user.
    
    This is the recommended endpoint for frontend seat clicking.
    """
    import logging
    from sqlmodel import select, and_
    from datetime import datetime
    from app.models.seat_reservation import SeatReservation
    
    logger = logging.getLogger(__name__)
    
    try:
        seat_ids = reservation_request.get_seat_ids()
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    # Check if user already has active reservations for these seats
    existing_reservations = session.exec(
        select(SeatReservation).where(
            and_(
                SeatReservation.screening_id == reservation_request.screening_id,
                SeatReservation.seat_id.in_(seat_ids),
                SeatReservation.user_id == current_user.id,
                SeatReservation.status == "active",
                SeatReservation.expires_at > datetime.utcnow()
            )
        )
    ).all()
    
    if existing_reservations:
        # User already reserved these seats - cancel them
        count, broadcast_updates = SeatReservationService.cancel_reservations(
            session=session,
            user_id=current_user.id,
            screening_id=reservation_request.screening_id,
            seat_ids=seat_ids
        )
        
        if broadcast_updates:
            background_tasks.add_task(broadcast_seat_updates, broadcast_updates)
        
        return {
            "action": "unreserved",
            "message": f"Unreserved {count} seat(s)",
            "seat_ids": seat_ids
        }
    else:
        # Reserve the seats
        reservations, broadcast_updates = SeatReservationService.reserve_seats(
            session=session,
            user_id=current_user.id,
            screening_id=reservation_request.screening_id,
            seat_ids=seat_ids
        )
        
        if broadcast_updates:
            background_tasks.add_task(broadcast_seat_updates, broadcast_updates)
        
        return {
            "action": "reserved",
            "message": f"Reserved {len(reservations)} seat(s) for {SeatReservationService.RESERVATION_DURATION_MINUTES} minutes",
            "seat_ids": seat_ids,
            "expires_in_minutes": SeatReservationService.RESERVATION_DURATION_MINUTES
        }


@router.post("/extend", response_model=SeatReservationResponse)
def extend_reservations(
    reservation_request: SeatReservationCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_session),
    additional_minutes: int = 5
):
    """
    Extend existing seat reservations.
    
    Allows users to extend their reservations if they need more time
    to complete the booking process.
    """
    try:
        seat_ids = reservation_request.get_seat_ids()
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    reservations, broadcast_updates = SeatReservationService.extend_reservation(
        session=session,
        user_id=current_user.id,
        screening_id=reservation_request.screening_id,
        seat_ids=seat_ids,
        additional_minutes=additional_minutes
    )
    
    # Schedule WebSocket broadcast as background task
    if broadcast_updates:
        background_tasks.add_task(broadcast_seat_updates, broadcast_updates)
    
    return SeatReservationResponse(
        reservations=reservations,
        expires_in_minutes=additional_minutes,
        message=f"Extended reservation for {len(reservations)} seats by {additional_minutes} minutes"
    )


@router.post("/cancel", status_code=status.HTTP_200_OK)
def cancel_specific_reservations(
    reservation_request: SeatReservationCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    """
    Cancel specific seat reservations for the current user.
    
    This endpoint allows users to unreserve seats they previously reserved.
    """
    try:
        seat_ids = reservation_request.get_seat_ids()
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    count, broadcast_updates = SeatReservationService.cancel_reservations(
        session=session,
        user_id=current_user.id,
        screening_id=reservation_request.screening_id,
        seat_ids=seat_ids
    )
    
    if count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active reservations found to cancel"
        )
    
    # Schedule WebSocket broadcast as background task
    if broadcast_updates:
        background_tasks.add_task(broadcast_seat_updates, broadcast_updates)
    
    return {
        "message": f"Cancelled {count} seat reservation(s)",
        "cancelled_count": count
    }


@router.delete("/cancel/{screening_id}", status_code=status.HTTP_204_NO_CONTENT)
def cancel_all_reservations(
    screening_id: int,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    """
    Cancel ALL seat reservations for the current user in a screening.
    
    Useful when user leaves the page or closes the browser.
    """
    count, broadcast_updates = SeatReservationService.cancel_reservations(
        session=session,
        user_id=current_user.id,
        screening_id=screening_id,
        seat_ids=None  # Cancel all
    )
    
    # Schedule WebSocket broadcast as background task (even if count is 0)
    if broadcast_updates:
        background_tasks.add_task(broadcast_seat_updates, broadcast_updates)
    
    return None


@router.get("/my-reservations", response_model=List[SeatReservationRead])
def get_my_reservations(
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_session),
    include_expired: bool = False
):
    """
    Get current user's seat reservations.
    
    By default, only returns active (non-expired) reservations.
    Set include_expired=true to include expired reservations.
    """
    reservations = SeatReservationService.get_user_reservations(
        session=session,
        user_id=current_user.id,
        include_expired=include_expired
    )
    
    return reservations


@router.post("/cleanup", status_code=status.HTTP_200_OK)
async def cleanup_expired_reservations(
    session: Session = Depends(get_session),
):
    """
    Manually trigger cleanup of expired seat reservations.
    
    This endpoint is useful for testing or manual cleanup.
    In production, this should run automatically via a background task.
    """
    from app.services.background_tasks import background_manager
    
    result = await background_manager.manual_cleanup()
    
    if result["success"]:
        return {
            "message": f"Cleaned up {result['cleaned_count']} expired reservations",
            "timestamp": result["timestamp"],
            "duration_seconds": result["duration_seconds"]
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Cleanup failed: {result['error']}"
        )