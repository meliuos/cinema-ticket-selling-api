"""Tests for ticket booking endpoints."""

from fastapi.testclient import TestClient


def test_book_tickets(client: TestClient, auth_headers, test_screening, test_seats):
    """Test booking tickets."""
    seat_ids = [test_seats[0].id, test_seats[1].id]
    response = client.post(
        "/api/v1/tickets/book",
        headers=auth_headers,
        json={
            "screening_id": test_screening.id,
            "seat_ids": seat_ids
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 2
    assert all(t["screening_id"] == test_screening.id for t in data)
    assert all(t["status"] == "booked" for t in data)


def test_book_tickets_no_auth(client: TestClient, test_screening, test_seats):
    """Test booking tickets without authentication fails."""
    response = client.post(
        "/api/v1/tickets/book",
        json={
            "screening_id": test_screening.id,
            "seat_ids": [test_seats[0].id]
        }
    )
    assert response.status_code == 401


def test_book_tickets_nonexistent_screening(client: TestClient, auth_headers, test_seats):
    """Test booking tickets for nonexistent screening fails."""
    response = client.post(
        "/api/v1/tickets/book",
        headers=auth_headers,
        json={
            "screening_id": 99999,
            "seat_ids": [test_seats[0].id]
        }
    )
    assert response.status_code == 404


def test_book_tickets_nonexistent_seat(client: TestClient, auth_headers, test_screening):
    """Test booking nonexistent seat fails."""
    response = client.post(
        "/api/v1/tickets/book",
        headers=auth_headers,
        json={
            "screening_id": test_screening.id,
            "seat_ids": [99999]
        }
    )
    assert response.status_code == 404


def test_book_tickets_wrong_room(client: TestClient, auth_headers, test_screening, session):
    """Test booking seats from wrong room fails."""
    from app.models import Room, Seat
    
    # Create a different room with a seat
    other_room = Room(name="Other Room", cinema_id=test_screening.room_id)
    session.add(other_room)
    session.commit()
    session.refresh(other_room)
    
    other_seat = Seat(room_id=other_room.id, row_label="Z", seat_number=99, seat_type="standard")
    session.add(other_seat)
    session.commit()
    session.refresh(other_seat)
    
    response = client.post(
        "/api/v1/tickets/book",
        headers=auth_headers,
        json={
            "screening_id": test_screening.id,
            "seat_ids": [other_seat.id]
        }
    )
    assert response.status_code == 400


def test_book_already_booked_seat(client: TestClient, auth_headers, test_screening, test_seats):
    """Test booking already booked seat fails."""
    # Book a seat first
    client.post(
        "/api/v1/tickets/book",
        headers=auth_headers,
        json={
            "screening_id": test_screening.id,
            "seat_ids": [test_seats[0].id]
        }
    )
    
    # Try to book the same seat again
    response = client.post(
        "/api/v1/tickets/book",
        headers=auth_headers,
        json={
            "screening_id": test_screening.id,
            "seat_ids": [test_seats[0].id]
        }
    )
    assert response.status_code == 400
    assert "already booked" in response.json()["detail"].lower()


def test_get_my_tickets(client: TestClient, auth_headers, test_screening, test_seats):
    """Test getting user's tickets."""
    # Book some tickets first
    client.post(
        "/api/v1/tickets/book",
        headers=auth_headers,
        json={
            "screening_id": test_screening.id,
            "seat_ids": [test_seats[0].id, test_seats[1].id]
        }
    )
    
    response = client.get("/api/v1/tickets/my-tickets", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 2


def test_get_my_tickets_no_auth(client: TestClient):
    """Test getting tickets without auth fails."""
    response = client.get("/api/v1/tickets/my-tickets")
    assert response.status_code == 401


def test_get_ticket(client: TestClient, auth_headers, test_screening, test_seats):
    """Test getting a specific ticket."""
    # Book a ticket first
    book_response = client.post(
        "/api/v1/tickets/book",
        headers=auth_headers,
        json={
            "screening_id": test_screening.id,
            "seat_ids": [test_seats[0].id]
        }
    )
    ticket_id = book_response.json()[0]["id"]
    
    response = client.get(f"/api/v1/tickets/{ticket_id}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == ticket_id


def test_get_ticket_wrong_user(client: TestClient, session, test_user, test_screening, test_seats):
    """Test getting another user's ticket fails."""
    from app.models import User, Ticket
    from app.services.auth import get_password_hash, create_access_token
    
    # Create another user
    other_user = User(
        email="other@example.com",
        full_name="Other User",
        hashed_password=get_password_hash("password123"),
        is_active=True
    )
    session.add(other_user)
    session.commit()
    session.refresh(other_user)
    
    # Create a ticket for the other user
    ticket = Ticket(
        user_id=other_user.id,
        screening_id=test_screening.id,
        seat_id=test_seats[0].id,
        price=15.0,
        status="booked"
    )
    session.add(ticket)
    session.commit()
    session.refresh(ticket)
    
    # Try to access with first user's token (test_user fixture)
    token = create_access_token(data={"sub": test_user.email})
    headers = {"Authorization": f"Bearer {token}"}
    
    response = client.get(f"/api/v1/tickets/{ticket.id}", headers=headers)
    assert response.status_code == 403


def test_cancel_ticket(client: TestClient, auth_headers, test_screening, test_seats):
    """Test cancelling a ticket."""
    # Book a ticket first
    book_response = client.post(
        "/api/v1/tickets/book",
        headers=auth_headers,
        json={
            "screening_id": test_screening.id,
            "seat_ids": [test_seats[0].id]
        }
    )
    ticket_id = book_response.json()[0]["id"]
    
    response = client.delete(f"/api/v1/tickets/{ticket_id}", headers=auth_headers)
    assert response.status_code == 204
    
    # Verify ticket is cancelled
    get_response = client.get(f"/api/v1/tickets/{ticket_id}", headers=auth_headers)
    assert get_response.json()["status"] == "cancelled"


def test_cancel_nonexistent_ticket(client: TestClient, auth_headers):
    """Test cancelling nonexistent ticket fails."""
    response = client.delete("/api/v1/tickets/99999", headers=auth_headers)
    assert response.status_code == 404


def test_cancel_ticket_no_auth(client: TestClient):
    """Test cancelling ticket without auth fails."""
    response = client.delete("/api/v1/tickets/1")
    assert response.status_code == 401
