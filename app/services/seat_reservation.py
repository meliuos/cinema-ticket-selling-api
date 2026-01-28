from __future__ import annotations

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

from sqlmodel import Session, select
from sqlalchemy import and_

from app.models.cinema import Seat, Room
from app.models.screening import Screening
from app.models.ticket import Ticket
from app.models.seat_reservation import SeatReservation
from app.schemas.seat_reservation import SeatAvailabilityRead, SeatRef


class SeatReservationService:
    """
    Minimal seat hold service used by Flutter/Angular seat selection.
    """

    RESERVATION_DURATION_MINUTES = 5

    @staticmethod
    def _now() -> datetime:
        return datetime.utcnow()

    @classmethod
    def _expires_at(cls) -> datetime:
        return cls._now() + timedelta(minutes=cls.RESERVATION_DURATION_MINUTES)

    @staticmethod
    def cleanup_expired(session: Session) -> int:
        """Mark expired active reservations as expired."""
        now = SeatReservationService._now()
        expired = session.exec(
            select(SeatReservation).where(
                and_(
                    SeatReservation.status == "active",
                    SeatReservation.expires_at <= now,
                )
            )
        ).all()
        for r in expired:
            r.status = "expired"
            session.add(r)
        if expired:
            session.commit()
        return len(expired)

    @staticmethod
    def _get_room_seats(session: Session, screening_id: int) -> List[Seat]:
        screening = session.get(Screening, screening_id)
        if not screening:
            return []
        return session.exec(select(Seat).where(Seat.room_id == screening.room_id)).all()

    @staticmethod
    def _get_booked_seat_ids(session: Session, screening_id: int) -> set[int]:
        # Treat booked/confirmed tickets as unavailable.
        rows = session.exec(
            select(Ticket.seat_id).where(
                and_(
                    Ticket.screening_id == screening_id,
                    Ticket.status.in_(["booked", "confirmed"]),
                )
            )
        ).all()
        return set(int(x) for x in rows)

    @staticmethod
    def _get_active_reservations(session: Session, screening_id: int) -> List[SeatReservation]:
        now = SeatReservationService._now()
        return session.exec(
            select(SeatReservation).where(
                and_(
                    SeatReservation.screening_id == screening_id,
                    SeatReservation.status == "active",
                    SeatReservation.expires_at > now,
                )
            )
        ).all()

    @classmethod
    def get_seat_availability(
        cls,
        session: Session,
        screening_id: int,
        current_user_id: Optional[int] = None,
    ) -> List[SeatAvailabilityRead]:
        cls.cleanup_expired(session)

        seats = cls._get_room_seats(session, screening_id)
        booked = cls._get_booked_seat_ids(session, screening_id)
        active = cls._get_active_reservations(session, screening_id)

        active_by_seat: Dict[int, SeatReservation] = {r.seat_id: r for r in active}

        out: List[SeatAvailabilityRead] = []
        for s in seats:
            if s.id is None:
                continue
            seat_ref = SeatRef(
                id=s.id,
                row_label=s.row_label,
                seat_number=s.seat_number,
                seat_type=s.seat_type,
            )

            if s.id in booked:
                out.append(
                    SeatAvailabilityRead(
                        seat_id=s.id,
                        status="booked",
                        reserved_by=None,
                        is_mine=False,
                        expires_at=None,
                        seat=seat_ref,
                    )
                )
                continue

            r = active_by_seat.get(s.id)
            if not r:
                out.append(
                    SeatAvailabilityRead(
                        seat_id=s.id,
                        status="available",
                        reserved_by=None,
                        is_mine=False,
                        expires_at=None,
                        seat=seat_ref,
                    )
                )
                continue

            is_mine = current_user_id is not None and r.user_id == current_user_id
            out.append(
                SeatAvailabilityRead(
                    seat_id=s.id,
                    status="reserved_by_me" if is_mine else "reserved",
                    reserved_by=r.user_id,
                    is_mine=is_mine,
                    expires_at=r.expires_at,
                    seat=seat_ref,
                )
            )

        return out

    @classmethod
    def toggle_seat(
        cls,
        session: Session,
        user_id: int,
        screening_id: int,
        seat_id: int,
    ) -> Tuple[str, List[int], Optional[int], Optional[SeatReservation]]:
        """
        Toggle a single seat:
        - if user already holds it (active), cancel
        - else create new active reservation if not booked/held by other
        """
        cls.cleanup_expired(session)
        now = cls._now()

        # Already booked?
        booked = session.exec(
            select(Ticket).where(
                and_(
                    Ticket.screening_id == screening_id,
                    Ticket.seat_id == seat_id,
                    Ticket.status.in_(["booked", "confirmed"]),
                )
            )
        ).first()
        if booked:
            raise ValueError("Seat is already booked")

        # User already holds it?
        existing = session.exec(
            select(SeatReservation).where(
                and_(
                    SeatReservation.screening_id == screening_id,
                    SeatReservation.seat_id == seat_id,
                    SeatReservation.user_id == user_id,
                    SeatReservation.status == "active",
                    SeatReservation.expires_at > now,
                )
            )
        ).first()
        if existing:
            existing.status = "cancelled"
            session.add(existing)
            session.commit()
            return ("unreserved", [seat_id], None, None)

        # Held by someone else?
        other = session.exec(
            select(SeatReservation).where(
                and_(
                    SeatReservation.screening_id == screening_id,
                    SeatReservation.seat_id == seat_id,
                    SeatReservation.status == "active",
                    SeatReservation.expires_at > now,
                )
            )
        ).first()
        if other and other.user_id != user_id:
            raise ValueError("Seat is reserved by another user")

        # Create hold
        res = SeatReservation(
            user_id=user_id,
            screening_id=screening_id,
            seat_id=seat_id,
            status="active",
            expires_at=cls._expires_at(),
        )
        session.add(res)
        session.commit()
        session.refresh(res)
        return ("reserved", [seat_id], cls.RESERVATION_DURATION_MINUTES, res)

    @classmethod
    def cancel_all_for_screening(cls, session: Session, user_id: int, screening_id: int) -> int:
        cls.cleanup_expired(session)
        now = cls._now()
        rows = session.exec(
            select(SeatReservation).where(
                and_(
                    SeatReservation.screening_id == screening_id,
                    SeatReservation.user_id == user_id,
                    SeatReservation.status == "active",
                    SeatReservation.expires_at > now,
                )
            )
        ).all()
        for r in rows:
            r.status = "cancelled"
            session.add(r)
        if rows:
            session.commit()
        return len(rows)

    @classmethod
    def extend_reservations(
        cls, session: Session, user_id: int, reservation_ids: List[int], extra_minutes: int
    ) -> List[SeatReservation]:
        cls.cleanup_expired(session)
        now = cls._now()
        rows = session.exec(
            select(SeatReservation).where(
                and_(
                    SeatReservation.id.in_(reservation_ids),
                    SeatReservation.user_id == user_id,
                    SeatReservation.status == "active",
                    SeatReservation.expires_at > now,
                )
            )
        ).all()
        if not rows:
            return []
        for r in rows:
            r.expires_at = r.expires_at + timedelta(minutes=extra_minutes)
            session.add(r)
        session.commit()
        for r in rows:
            session.refresh(r)
        return rows
