"""Tests for screening endpoints."""

from fastapi.testclient import TestClient
from datetime import datetime, timedelta


def test_create_screening(client: TestClient, test_movie, test_room, admin_headers):
    """Test creating a screening."""
    future_time = (datetime.utcnow() + timedelta(days=2)).isoformat()
    response = client.post(
        "/api/v1/screenings/",
        json={
            "movie_id": test_movie.id,
            "room_id": test_room.id,
            "screening_time": future_time,
            "price": 20.0
        },
        headers=admin_headers
    )
    assert response.status_code == 201
    data = response.json()
    assert data["movie_id"] == test_movie.id
    assert data["room_id"] == test_room.id
    assert data["price"] == 20.0


def test_create_screening_nonexistent_movie(client: TestClient, test_room, admin_headers):
    """Test creating screening with nonexistent movie fails."""
    future_time = (datetime.utcnow() + timedelta(days=2)).isoformat()
    response = client.post(
        "/api/v1/screenings/",
        json={
            "movie_id": 99999,
            "room_id": test_room.id,
            "screening_time": future_time,
            "price": 20.0
        },
        headers=admin_headers
    )
    assert response.status_code == 404


def test_create_screening_nonexistent_room(client: TestClient, test_movie, admin_headers):
    """Test creating screening with nonexistent room fails."""
    future_time = (datetime.utcnow() + timedelta(days=2)).isoformat()
    response = client.post(
        "/api/v1/screenings/",
        json={
            "movie_id": test_movie.id,
            "room_id": 99999,
            "screening_time": future_time,
            "price": 20.0
        },
        headers=admin_headers
    )
    assert response.status_code == 404


def test_list_screenings(client: TestClient, test_screening):
    """Test listing all screenings."""
    response = client.get("/api/v1/screenings/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert any(s["id"] == test_screening.id for s in data)


def test_list_screenings_filter_by_movie(client: TestClient, test_screening, test_movie):
    """Test listing screenings filtered by movie."""
    response = client.get(f"/api/v1/screenings/?movie_id={test_movie.id}")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert all(s["movie_id"] == test_movie.id for s in data)


def test_list_screenings_filter_by_room(client: TestClient, test_screening, test_room):
    """Test listing screenings filtered by room."""
    response = client.get(f"/api/v1/screenings/?room_id={test_room.id}")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert all(s["room_id"] == test_room.id for s in data)


def test_list_screenings_filter_by_cinema(client: TestClient, test_screening, test_cinema):
    """Test listing screenings filtered by cinema."""
    response = client.get(f"/api/v1/screenings/?cinema_id={test_cinema.id}")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_get_screening(client: TestClient, test_screening):
    """Test getting a specific screening."""
    response = client.get(f"/api/v1/screenings/{test_screening.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_screening.id
    assert data["screening_time"]
    assert data["price"] == test_screening.price
    # Check that movie details are included
    assert "movie" in data
    assert data["movie"]["id"] == test_screening.movie_id
    assert "title" in data["movie"]
    assert "description" in data["movie"]
    # Check that room details are included
    assert "room" in data
    assert data["room"]["id"] == test_screening.room_id
    assert "cinema" in data["room"]


def test_get_nonexistent_screening(client: TestClient):
    """Test getting a nonexistent screening fails."""
    response = client.get("/api/v1/screenings/99999")
    assert response.status_code == 404


def test_get_available_seats(client: TestClient, test_screening, test_seats):
    """Test getting available seats for a screening."""
    response = client.get(f"/api/v1/screenings/{test_screening.id}/available-seats")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    # All seats should be available initially
    assert len(data) >= len(test_seats)


def test_get_available_seats_nonexistent_screening(client: TestClient):
    """Test getting available seats for nonexistent screening fails."""
    response = client.get("/api/v1/screenings/99999/available-seats")
    assert response.status_code == 404
