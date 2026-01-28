"""Seat reservation routes (temporary seat locking)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from typing import List

from app.config import settings
from app.database import get_session
from app.models.user import User
from app.schemas.seat_reservation import (
    SeatAvailabilityRead,
    SeatReservationCreate,
    SeatReservationResponse,
)
from app.services.auth import get_current_active_user
from app.services.seat_reservation import SeatReservationService
from app.services.websocket_manager import manager

router = APIRouter(
    prefix=f"{settings.API_V1_PREFIX}/seat-reservations",
    tags=["Seat Reservations"],
)


@router.get(
    "/screening/{screening_id}/availability",
    response_model=List[SeatAvailabilityRead],
)
def get_seat_availability(
    screening_id: int,
    session: Session = Depends(get_session),
):
    return SeatReservationService.get_seat_availability(session, screening_id)


@router.get(
    "/screening/{screening_id}/availability/me",
    response_model=List[SeatAvailabilityRead],
)
def get_seat_availability_for_user(
    screening_id: int,
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_session),
):
    return SeatReservationService.get_seat_availability(
        session,
        screening_id,
        current_user_id=current_user.id,
    )


@router.post("/toggle", status_code=status.HTTP_200_OK)
async def toggle_seat_reservation(
    reservation_request: SeatReservationCreate,
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_session),
):
    try:
        seat_ids = reservation_request.get_seat_ids()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if len(seat_ids) != 1:
        raise HTTPException(status_code=400, detail="toggle expects exactly one seat_id")

    seat_id = int(seat_ids[0])
    try:
        action, seat_ids_out, expires_in, reservation = SeatReservationService.toggle_seat(
            session=session,
            user_id=current_user.id,
            screening_id=reservation_request.screening_id,
            seat_id=seat_id,
        )
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))

    # Broadcast WS update
    if action == "reserved":
        await manager.broadcast_seat_update(
            reservation_request.screening_id,
            seat_id=seat_id,
            status="reserved_by_me",
            reserved_by=current_user.id,
            is_mine=True,
        )
    else:
        await manager.broadcast_seat_update(
            reservation_request.screening_id,
            seat_id=seat_id,
            status="available",
            reserved_by=None,
            is_mine=False,
        )

    body = {
        "action": action,
        "message": "ok",
        "seat_ids": seat_ids_out,
    }
    if expires_in is not None:
        body["expires_in_minutes"] = expires_in
    if reservation is not None:
        body["reservation"] = {
            "id": reservation.id,
            "screening_id": reservation.screening_id,
            "seat_id": reservation.seat_id,
            "user_id": reservation.user_id,
            "status": "held",
            "expires_at": reservation.expires_at.isoformat(),
        }
    return body


@router.delete("/cancel/{screening_id}", status_code=status.HTTP_200_OK)
async def cancel_all_reservations(
    screening_id: int,
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_session),
):
    count = SeatReservationService.cancel_all_for_screening(session, current_user.id, screening_id)
    # Broadcast availability to others (best-effort)
    # Note: we don't know all seat_ids here without re-querying, so clients should reload.
    return {"message": f"Cancelled {count} reservation(s)"}


@router.post("/extend", response_model=SeatReservationResponse, status_code=status.HTTP_200_OK)
async def extend_reservations(
    reservation_request: dict,
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_session),
):
    # Accepts { reservation_ids: [...], extra_minutes: 5 }
    reservation_ids = [int(x) for x in (reservation_request.get("reservation_ids") or [])]
    extra_minutes = int(reservation_request.get("extra_minutes") or 5)
    rows = SeatReservationService.extend_reservations(session, current_user.id, reservation_ids, extra_minutes)
    return SeatReservationResponse(
        reservations=[
            {
                "id": r.id,
                "user_id": r.user_id,
                "screening_id": r.screening_id,
                "seat_id": r.seat_id,
                "status": r.status,
                "created_at": r.created_at,
                "expires_at": r.expires_at,
            }
            for r in rows
        ],
        expires_in_minutes=extra_minutes,
        message=f"Extended {len(rows)} reservation(s) by {extra_minutes} minutes",
    )

