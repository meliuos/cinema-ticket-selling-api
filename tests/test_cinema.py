"""Tests for cinema and room endpoints."""

from fastapi.testclient import TestClient
from sqlmodel import Session


def test_create_cinema(client: TestClient, admin_headers):
    """Test creating a cinema."""
    response = client.post(
        "/api/v1/cinemas/",
        json={
            "name": "New Cinema",
            "address": "123 Main St",
            "city": "New York"
        },
        headers=admin_headers
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


def test_create_room(client: TestClient, test_cinema, admin_headers):
    """Test creating a room in a cinema."""
    response = client.post(
        f"/api/v1/cinemas/{test_cinema.id}/rooms/",
        json={"name": "IMAX Room"},
        headers=admin_headers
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "IMAX Room"
    assert data["cinema_id"] == test_cinema.id
    assert "id" in data


def test_create_room_nonexistent_cinema(client: TestClient, admin_headers):
    """Test creating a room in nonexistent cinema fails."""
    response = client.post(
        "/api/v1/cinemas/99999/rooms/",
        json={"name": "Test Room"},
        headers=admin_headers
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


def test_bulk_create_seats(client: TestClient, test_room, admin_headers):
    """Test bulk creating seats."""
    response = client.post(
        f"/api/v1/rooms/{test_room.id}/seats/bulk",
        json={
            "rows": 5,
            "seats_per_row": 10,
            "seat_type": "standard"
        },
        headers=admin_headers
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


# ============= Cinema Search Tests =============

def test_search_cinemas_by_name(client: TestClient, test_cinema):
    """Test searching cinemas by name."""
    response = client.get(f"/api/v1/cinemas/search?q={test_cinema.name[:4]}")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert any(c["id"] == test_cinema.id for c in data)


def test_search_cinemas_by_city(client: TestClient, test_cinema):
    """Test searching cinemas by city."""
    response = client.get(f"/api/v1/cinemas/search?q={test_cinema.city}")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


def test_search_cinemas_no_results(client: TestClient):
    """Test cinema search with no results."""
    response = client.get("/api/v1/cinemas/search?q=NonexistentCinemaXYZ123")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 0


def test_search_cinemas_case_insensitive(client: TestClient, test_cinema):
    """Test cinema search is case-insensitive."""
    response = client.get(f"/api/v1/cinemas/search?q={test_cinema.name.upper()}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1


# ============= Cinema Amenities Tests =============

def test_get_cinema_amenities(client: TestClient, test_cinema):
    """Test getting cinema amenities."""
    response = client.get(f"/api/v1/cinemas/{test_cinema.id}/amenities")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert data == test_cinema.amenities


def test_get_amenities_empty(client: TestClient, session):
    """Test getting amenities for cinema without amenities."""
    from app.models import Cinema
    cinema = Cinema(
        name="No Amenities Cinema",
        address="456 Side St",
        city="Chicago",
        amenities=[]
    )
    session.add(cinema)
    session.commit()
    session.refresh(cinema)
    
    response = client.get(f"/api/v1/cinemas/{cinema.id}/amenities")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 0


def test_get_amenities_nonexistent_cinema(client: TestClient):
    """Test getting amenities for nonexistent cinema fails."""
    response = client.get("/api/v1/cinemas/99999/amenities")
    assert response.status_code == 404


# ============= Cinema Movies Tests =============

def test_get_cinema_movies(client: TestClient, test_cinema, test_movie, test_screening):
    """Test getting movies showing at a cinema."""
    response = client.get(f"/api/v1/cinemas/{test_cinema.id}/movies")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    # Check if test movie is in the list
    assert any(m["id"] == test_movie.id for m in data)


def test_get_cinema_movies_no_screenings(client: TestClient, session):
    """Test getting movies for cinema with no screenings."""
    from app.models import Cinema
    cinema = Cinema(
        name="Empty Cinema",
        address="789 Empty St",
        city="Boston"
    )
    session.add(cinema)
    session.commit()
    session.refresh(cinema)
    
    response = client.get(f"/api/v1/cinemas/{cinema.id}/movies")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 0


def test_get_cinema_movies_nonexistent(client: TestClient):
    """Test getting movies for nonexistent cinema fails."""
    response = client.get("/api/v1/cinemas/99999/movies")
    assert response.status_code == 404


# ============= Cinema Showtimes Tests =============

def test_get_cinema_showtimes(client: TestClient, test_cinema, test_screening):
    """Test getting cinema showtimes."""
    response = client.get(f"/api/v1/cinemas/{test_cinema.id}/showtimes")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert any(s["id"] == test_screening.id for s in data)


def test_get_cinema_showtimes_with_date(client: TestClient, test_cinema, test_screening):
    """Test getting cinema showtimes filtered by date."""
    screening_date = test_screening.screening_time.date().isoformat()
    
    response = client.get(f"/api/v1/cinemas/{test_cinema.id}/showtimes?date={screening_date}")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


def test_get_cinema_showtimes_wrong_date(client: TestClient, test_cinema):
    """Test getting cinema showtimes for date with no screenings."""
    response = client.get(f"/api/v1/cinemas/{test_cinema.id}/showtimes?date=2030-12-31")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 0


def test_get_cinema_showtimes_nonexistent(client: TestClient):
    """Test getting showtimes for nonexistent cinema fails."""
    response = client.get("/api/v1/cinemas/99999/showtimes")
    assert response.status_code == 404

