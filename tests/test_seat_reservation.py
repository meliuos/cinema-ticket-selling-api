"""Tests for seat reservation endpoints."""

import pytest
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from sqlmodel import Session

from app.models import User, Cinema, Room, Seat, Movie, Screening
from app.models.seat_reservation import SeatReservation


class TestSeatAvailability:
    """Tests for seat availability endpoint."""
    
    def test_get_seat_availability(
        self, 
        client: TestClient, 
        session: Session,
        test_screening: Screening,
        test_seats: list[Seat]
    ):
        """Test getting seat availability for a screening."""
        response = client.get(
            f"/api/v1/seat-reservations/screening/{test_screening.id}/availability"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == len(test_seats)
        
        # Check first seat structure
        first_seat = data[0]
        assert "seat" in first_seat
        assert "status" in first_seat
        assert first_seat["status"] == "available"
        assert first_seat["reserved_by"] is None
        assert first_seat["expires_at"] is None
    
    def test_get_seat_availability_nonexistent_screening(self, client: TestClient):
        """Test getting availability for non-existent screening."""
        response = client.get(
            "/api/v1/seat-reservations/screening/99999/availability"
        )
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()


class TestSeatReservation:
    """Tests for seat reservation endpoints."""
    
    def test_reserve_single_seat(
        self,
        client: TestClient,
        session: Session,
        test_screening: Screening,
        test_seats: list[Seat],
        auth_headers: dict
    ):
        """Test reserving a single seat."""
        seat = test_seats[0]
        
        response = client.post(
            "/api/v1/seat-reservations/reserve",
            json={
                "screening_id": test_screening.id,
                "seat_id": seat.id
            },
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "reservations" in data
        assert len(data["reservations"]) == 1
        assert data["reservations"][0]["seat_id"] == seat.id
        assert data["reservations"][0]["status"] == "active"
        assert data["expires_in_minutes"] == 5
    
    def test_reserve_multiple_seats(
        self,
        client: TestClient,
        session: Session,
        test_screening: Screening,
        test_seats: list[Seat],
        auth_headers: dict
    ):
        """Test reserving multiple seats."""
        seat_ids = [test_seats[0].id, test_seats[1].id, test_seats[2].id]
        
        response = client.post(
            "/api/v1/seat-reservations/reserve",
            json={
                "screening_id": test_screening.id,
                "seat_ids": seat_ids
            },
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert len(data["reservations"]) == 3
        reserved_seat_ids = [r["seat_id"] for r in data["reservations"]]
        assert set(reserved_seat_ids) == set(seat_ids)
    
    def test_reserve_already_reserved_seat(
        self,
        client: TestClient,
        session: Session,
        test_screening: Screening,
        test_seats: list[Seat],
        auth_headers: dict,
        admin_headers: dict
    ):
        """Test reserving a seat that's already reserved by another user."""
        seat = test_seats[0]
        
        # First user reserves the seat
        response1 = client.post(
            "/api/v1/seat-reservations/reserve",
            json={
                "screening_id": test_screening.id,
                "seat_id": seat.id
            },
            headers=auth_headers
        )
        assert response1.status_code == 200
        
        # Second user tries to reserve the same seat
        response2 = client.post(
            "/api/v1/seat-reservations/reserve",
            json={
                "screening_id": test_screening.id,
                "seat_id": seat.id
            },
            headers=admin_headers
        )
        
        assert response2.status_code == 409
        assert "reserved by other users" in response2.json()["detail"].lower()
    
    def test_reserve_same_seat_same_user(
        self,
        client: TestClient,
        session: Session,
        test_screening: Screening,
        test_seats: list[Seat],
        auth_headers: dict
    ):
        """Test that same user can re-reserve their own seat (updates expiry)."""
        seat = test_seats[0]
        
        # First reservation
        response1 = client.post(
            "/api/v1/seat-reservations/reserve",
            json={
                "screening_id": test_screening.id,
                "seat_id": seat.id
            },
            headers=auth_headers
        )
        assert response1.status_code == 200
        first_id = response1.json()["reservations"][0]["id"]
        
        # Second reservation (should cancel first and create new)
        response2 = client.post(
            "/api/v1/seat-reservations/reserve",
            json={
                "screening_id": test_screening.id,
                "seat_id": seat.id
            },
            headers=auth_headers
        )
        assert response2.status_code == 200
        second_id = response2.json()["reservations"][0]["id"]
        
        # Should create a new reservation (different ID)
        assert second_id != first_id
    
    def test_reserve_nonexistent_seat(
        self,
        client: TestClient,
        test_screening: Screening,
        auth_headers: dict
    ):
        """Test reserving a non-existent seat."""
        response = client.post(
            "/api/v1/seat-reservations/reserve",
            json={
                "screening_id": test_screening.id,
                "seat_id": 99999
            },
            headers=auth_headers
        )
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_reserve_without_auth(
        self,
        client: TestClient,
        test_screening: Screening,
        test_seats: list[Seat]
    ):
        """Test reserving without authentication."""
        response = client.post(
            "/api/v1/seat-reservations/reserve",
            json={
                "screening_id": test_screening.id,
                "seat_id": test_seats[0].id
            }
        )
        
        assert response.status_code == 401
    
    def test_reserve_past_screening(
        self,
        client: TestClient,
        session: Session,
        test_movie: Movie,
        test_room: Room,
        test_seats: list[Seat],
        auth_headers: dict
    ):
        """Test reserving seats for a past screening."""
        # Create a past screening
        past_screening = Screening(
            movie_id=test_movie.id,
            room_id=test_room.id,
            screening_time=datetime.utcnow() - timedelta(days=1),
            price=15.0
        )
        session.add(past_screening)
        session.commit()
        session.refresh(past_screening)
        
        response = client.post(
            "/api/v1/seat-reservations/reserve",
            json={
                "screening_id": past_screening.id,
                "seat_id": test_seats[0].id
            },
            headers=auth_headers
        )
        
        assert response.status_code == 400
        assert "past screening" in response.json()["detail"].lower()


class TestToggleReservation:
    """Tests for toggle reservation endpoint."""
    
    def test_toggle_reserve_available_seat(
        self,
        client: TestClient,
        test_screening: Screening,
        test_seats: list[Seat],
        auth_headers: dict
    ):
        """Test toggling an available seat (should reserve it)."""
        seat = test_seats[0]
        
        response = client.post(
            "/api/v1/seat-reservations/toggle",
            json={
                "screening_id": test_screening.id,
                "seat_id": seat.id
            },
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["action"] == "reserved"
        assert seat.id in data["seat_ids"]
        assert "expires_in_minutes" in data
    
    def test_toggle_unreserve_reserved_seat(
        self,
        client: TestClient,
        test_screening: Screening,
        test_seats: list[Seat],
        auth_headers: dict
    ):
        """Test toggling a reserved seat (should unreserve it)."""
        seat = test_seats[0]
        
        # First, reserve the seat
        response1 = client.post(
            "/api/v1/seat-reservations/toggle",
            json={
                "screening_id": test_screening.id,
                "seat_id": seat.id
            },
            headers=auth_headers
        )
        assert response1.status_code == 200
        assert response1.json()["action"] == "reserved"
        
        # Then, toggle again to unreserve
        response2 = client.post(
            "/api/v1/seat-reservations/toggle",
            json={
                "screening_id": test_screening.id,
                "seat_id": seat.id
            },
            headers=auth_headers
        )
        
        assert response2.status_code == 200
        data = response2.json()
        
        assert data["action"] == "unreserved"
        assert seat.id in data["seat_ids"]
    
    def test_toggle_multiple_seats(
        self,
        client: TestClient,
        test_screening: Screening,
        test_seats: list[Seat],
        auth_headers: dict
    ):
        """Test toggling multiple seats at once."""
        seat_ids = [test_seats[0].id, test_seats[1].id]
        
        # Reserve both
        response1 = client.post(
            "/api/v1/seat-reservations/toggle",
            json={
                "screening_id": test_screening.id,
                "seat_ids": seat_ids
            },
            headers=auth_headers
        )
        assert response1.status_code == 200
        assert response1.json()["action"] == "reserved"
        
        # Unreserve both
        response2 = client.post(
            "/api/v1/seat-reservations/toggle",
            json={
                "screening_id": test_screening.id,
                "seat_ids": seat_ids
            },
            headers=auth_headers
        )
        assert response2.status_code == 200
        assert response2.json()["action"] == "unreserved"


class TestCancelReservation:
    """Tests for cancel reservation endpoints."""
    
    def test_cancel_specific_seats(
        self,
        client: TestClient,
        test_screening: Screening,
        test_seats: list[Seat],
        auth_headers: dict
    ):
        """Test canceling specific seat reservations."""
        seat = test_seats[0]
        
        # Reserve the seat
        client.post(
            "/api/v1/seat-reservations/reserve",
            json={
                "screening_id": test_screening.id,
                "seat_id": seat.id
            },
            headers=auth_headers
        )
        
        # Cancel it
        response = client.post(
            "/api/v1/seat-reservations/cancel",
            json={
                "screening_id": test_screening.id,
                "seat_id": seat.id
            },
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "cancelled_count" in data
        assert data["cancelled_count"] == 1
    
    def test_cancel_all_user_reservations(
        self,
        client: TestClient,
        test_screening: Screening,
        test_seats: list[Seat],
        auth_headers: dict
    ):
        """Test canceling all reservations for a user in a screening."""
        # Reserve multiple seats
        seat_ids = [test_seats[0].id, test_seats[1].id, test_seats[2].id]
        client.post(
            "/api/v1/seat-reservations/reserve",
            json={
                "screening_id": test_screening.id,
                "seat_ids": seat_ids
            },
            headers=auth_headers
        )
        
        # Cancel all
        response = client.delete(
            f"/api/v1/seat-reservations/cancel/{test_screening.id}",
            headers=auth_headers
        )
        
        assert response.status_code == 204
    
    def test_cancel_nonexistent_reservation(
        self,
        client: TestClient,
        test_screening: Screening,
        test_seats: list[Seat],
        auth_headers: dict
    ):
        """Test canceling a reservation that doesn't exist."""
        response = client.post(
            "/api/v1/seat-reservations/cancel",
            json={
                "screening_id": test_screening.id,
                "seat_id": test_seats[0].id
            },
            headers=auth_headers
        )
        
        assert response.status_code == 404
    
    def test_cancel_other_user_reservation(
        self,
        client: TestClient,
        test_screening: Screening,
        test_seats: list[Seat],
        auth_headers: dict,
        admin_headers: dict
    ):
        """Test that user cannot cancel another user's reservation."""
        seat = test_seats[0]
        
        # User 1 reserves
        client.post(
            "/api/v1/seat-reservations/reserve",
            json={
                "screening_id": test_screening.id,
                "seat_id": seat.id
            },
            headers=auth_headers
        )
        
        # User 2 tries to cancel
        response = client.post(
            "/api/v1/seat-reservations/cancel",
            json={
                "screening_id": test_screening.id,
                "seat_id": seat.id
            },
            headers=admin_headers
        )
        
        assert response.status_code == 404


class TestExtendReservation:
    """Tests for extend reservation endpoint."""
    
    def test_extend_reservation(
        self,
        client: TestClient,
        test_screening: Screening,
        test_seats: list[Seat],
        auth_headers: dict
    ):
        """Test extending a reservation."""
        seat = test_seats[0]
        
        # Reserve the seat
        response1 = client.post(
            "/api/v1/seat-reservations/reserve",
            json={
                "screening_id": test_screening.id,
                "seat_id": seat.id
            },
            headers=auth_headers
        )
        assert response1.status_code == 200
        original_expires = response1.json()["reservations"][0]["expires_at"]
        
        # Extend it
        response2 = client.post(
            "/api/v1/seat-reservations/extend?additional_minutes=5",
            json={
                "screening_id": test_screening.id,
                "seat_id": seat.id
            },
            headers=auth_headers
        )
        
        assert response2.status_code == 200
        data = response2.json()
        
        assert len(data["reservations"]) == 1
        new_expires = data["reservations"][0]["expires_at"]
        
        # New expiry should be later than original
        assert new_expires > original_expires
    
    def test_extend_nonexistent_reservation(
        self,
        client: TestClient,
        test_screening: Screening,
        test_seats: list[Seat],
        auth_headers: dict
    ):
        """Test extending a reservation that doesn't exist."""
        response = client.post(
            "/api/v1/seat-reservations/extend",
            json={
                "screening_id": test_screening.id,
                "seat_id": test_seats[0].id
            },
            headers=auth_headers
        )
        
        assert response.status_code == 400


class TestMyReservations:
    """Tests for getting user's reservations."""
    
    def test_get_my_reservations(
        self,
        client: TestClient,
        test_screening: Screening,
        test_seats: list[Seat],
        auth_headers: dict
    ):
        """Test getting current user's reservations."""
        # Reserve some seats
        seat_ids = [test_seats[0].id, test_seats[1].id]
        client.post(
            "/api/v1/seat-reservations/reserve",
            json={
                "screening_id": test_screening.id,
                "seat_ids": seat_ids
            },
            headers=auth_headers
        )
        
        # Get reservations
        response = client.get(
            "/api/v1/seat-reservations/my-reservations",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
        assert len(data) == 2
    
    def test_get_my_reservations_empty(
        self,
        client: TestClient,
        auth_headers: dict
    ):
        """Test getting reservations when user has none."""
        response = client.get(
            "/api/v1/seat-reservations/my-reservations",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        assert response.json() == []


class TestExpiredReservations:
    """Tests for expired reservation cleanup."""
    
    def test_expired_reservations_are_cleaned(
        self,
        client: TestClient,
        session: Session,
        test_screening: Screening,
        test_seats: list[Seat],
        test_user: User
    ):
        """Test that expired reservations are automatically cleaned up."""
        seat = test_seats[0]
        
        # Create an expired reservation manually
        expired_reservation = SeatReservation(
            screening_id=test_screening.id,
            seat_id=seat.id,
            user_id=test_user.id,
            reserved_at=datetime.utcnow() - timedelta(minutes=10),
            expires_at=datetime.utcnow() - timedelta(minutes=5),
            status="active"
        )
        session.add(expired_reservation)
        session.commit()
        
        # Get availability (should trigger cleanup)
        response = client.get(
            f"/api/v1/seat-reservations/screening/{test_screening.id}/availability"
        )
        
        assert response.status_code == 200
        
        # Check that the seat is now available
        seats_data = response.json()
        expired_seat = next(s for s in seats_data if s["seat"]["id"] == seat.id)
        assert expired_seat["status"] == "available"


class TestConcurrentReservations:
    """Tests for concurrent reservation scenarios."""
    
    def test_concurrent_reservation_handling(
        self,
        client: TestClient,
        test_screening: Screening,
        test_seats: list[Seat],
        auth_headers: dict,
        admin_headers: dict
    ):
        """Test that concurrent reservations are handled correctly."""
        seat = test_seats[0]
        
        # User 1 reserves
        response1 = client.post(
            "/api/v1/seat-reservations/reserve",
            json={
                "screening_id": test_screening.id,
                "seat_id": seat.id
            },
            headers=auth_headers
        )
        assert response1.status_code == 200
        
        # User 2 tries immediately after
        response2 = client.post(
            "/api/v1/seat-reservations/reserve",
            json={
                "screening_id": test_screening.id,
                "seat_id": seat.id
            },
            headers=admin_headers
        )
        
        # Should fail with conflict
        assert response2.status_code == 409


class TestValidationErrors:
    """Tests for validation errors."""
    
    def test_missing_screening_id(
        self,
        client: TestClient,
        test_seats: list[Seat],
        auth_headers: dict
    ):
        """Test reserving without screening_id."""
        response = client.post(
            "/api/v1/seat-reservations/reserve",
            json={
                "seat_id": test_seats[0].id
            },
            headers=auth_headers
        )
        
        assert response.status_code == 422
    
    def test_missing_seat_id_and_seat_ids(
        self,
        client: TestClient,
        test_screening: Screening,
        auth_headers: dict
    ):
        """Test reserving without seat_id or seat_ids."""
        response = client.post(
            "/api/v1/seat-reservations/reserve",
            json={
                "screening_id": test_screening.id
            },
            headers=auth_headers
        )
        
        assert response.status_code == 400
        assert "seat_id" in response.json()["detail"].lower()
    
    def test_invalid_screening_id(
        self,
        client: TestClient,
        test_seats: list[Seat],
        auth_headers: dict
    ):
        """Test reserving with invalid screening_id."""
        response = client.post(
            "/api/v1/seat-reservations/reserve",
            json={
                "screening_id": 99999,
                "seat_id": test_seats[0].id
            },
            headers=auth_headers
        )
        
        assert response.status_code == 404
