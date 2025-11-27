"""Tests for showtime endpoints."""

from fastapi.testclient import TestClient
from datetime import datetime


def test_list_all_showtimes(client: TestClient, test_screening):
    """Test listing all showtimes."""
    response = client.get("/api/v1/showtimes/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert any(s["id"] == test_screening.id for s in data)


def test_list_showtimes_with_date_filter(client: TestClient, test_screening):
    """Test listing showtimes filtered by date."""
    screening_date = test_screening.screening_time.date().isoformat()
    
    response = client.get(f"/api/v1/showtimes/?date={screening_date}")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


def test_list_showtimes_with_movie_filter(client: TestClient, test_movie, test_screening):
    """Test listing showtimes filtered by movie."""
    response = client.get(f"/api/v1/showtimes/?movie_id={test_movie.id}")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert all(s["movie_id"] == test_movie.id for s in data)


def test_list_showtimes_with_cinema_filter(client: TestClient, test_cinema, test_screening):
    """Test listing showtimes filtered by cinema."""
    response = client.get(f"/api/v1/showtimes/?cinema_id={test_cinema.id}")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


def test_list_showtimes_with_multiple_filters(client: TestClient, test_movie, test_cinema, test_screening):
    """Test listing showtimes with multiple filters."""
    screening_date = test_screening.screening_time.date().isoformat()
    
    response = client.get(
        f"/api/v1/showtimes/?date={screening_date}&movie_id={test_movie.id}&cinema_id={test_cinema.id}"
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


def test_list_showtimes_no_results(client: TestClient):
    """Test listing showtimes with filters that match nothing."""
    response = client.get("/api/v1/showtimes/?date=2030-12-31")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 0


def test_get_showtime_by_id(client: TestClient, test_screening):
    """Test getting a specific showtime by ID."""
    response = client.get(f"/api/v1/showtimes/{test_screening.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_screening.id
    assert data["movie_id"] == test_screening.movie_id


def test_get_nonexistent_showtime(client: TestClient):
    """Test getting a nonexistent showtime fails."""
    response = client.get("/api/v1/showtimes/99999")
    assert response.status_code == 404


def test_get_showtime_seats(client: TestClient, test_screening, test_seats):
    """Test getting available seats for a showtime."""
    response = client.get(f"/api/v1/showtimes/{test_screening.id}/seats")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= len(test_seats)
    # Check seat structure
    if len(data) > 0:
        assert "id" in data[0]
        assert "row_label" in data[0]
        assert "seat_number" in data[0]


def test_get_showtime_seats_nonexistent(client: TestClient):
    """Test getting seats for nonexistent showtime fails."""
    response = client.get("/api/v1/showtimes/99999/seats")
    assert response.status_code == 404
