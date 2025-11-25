"""Tests for cinema and room endpoints."""

from fastapi.testclient import TestClient
from sqlmodel import Session


def test_create_cinema(client: TestClient):
    """Test creating a cinema."""
    response = client.post(
        "/api/v1/cinemas/",
        json={
            "name": "New Cinema",
            "address": "123 Main St",
            "city": "New York"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "New Cinema"
    assert data["address"] == "123 Main St"
    assert data["city"] == "New York"
    assert "id" in data


def test_list_cinemas(client: TestClient, test_cinema):
    """Test listing cinemas."""
    response = client.get("/api/v1/cinemas/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert any(c["id"] == test_cinema.id for c in data)


def test_get_cinema(client: TestClient, test_cinema):
    """Test getting a specific cinema."""
    response = client.get(f"/api/v1/cinemas/{test_cinema.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_cinema.id
    assert data["name"] == test_cinema.name


def test_get_nonexistent_cinema(client: TestClient):
    """Test getting a nonexistent cinema fails."""
    response = client.get("/api/v1/cinemas/99999")
    assert response.status_code == 404


def test_create_room(client: TestClient, test_cinema):
    """Test creating a room in a cinema."""
    response = client.post(
        f"/api/v1/cinemas/{test_cinema.id}/rooms/",
        json={"name": "IMAX Room"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "IMAX Room"
    assert data["cinema_id"] == test_cinema.id
    assert "id" in data


def test_create_room_nonexistent_cinema(client: TestClient):
    """Test creating a room in nonexistent cinema fails."""
    response = client.post(
        "/api/v1/cinemas/99999/rooms/",
        json={"name": "Test Room"}
    )
    assert response.status_code == 404


def test_list_cinema_rooms(client: TestClient, test_cinema, test_room):
    """Test listing rooms in a cinema."""
    response = client.get(f"/api/v1/cinemas/{test_cinema.id}/rooms/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert any(r["id"] == test_room.id for r in data)


def test_get_room(client: TestClient, test_room):
    """Test getting a specific room."""
    response = client.get(f"/api/v1/rooms/{test_room.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_room.id
    assert data["name"] == test_room.name


def test_bulk_create_seats(client: TestClient, test_room):
    """Test bulk creating seats."""
    response = client.post(
        f"/api/v1/rooms/{test_room.id}/seats/bulk",
        json={
            "rows": 5,
            "seats_per_row": 10,
            "seat_type": "standard"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 50  # 5 rows x 10 seats


def test_list_room_seats(client: TestClient, test_room, test_seats):
    """Test listing seats in a room."""
    response = client.get(f"/api/v1/rooms/{test_room.id}/seats/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= len(test_seats)
