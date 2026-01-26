"""Tests for movie endpoints."""

from fastapi.testclient import TestClient
from datetime import date


def test_create_movie_basic(client: TestClient, admin_headers):
    """Test creating a movie with basic fields."""
    response = client.post(
        "/api/v1/movies/",
        json={
            "title": "New Movie",
            "description": "A new movie",
            "duration_minutes": 120,
            "genre": ["Drama"],
            "rating": "PG-13"
        },
        headers=admin_headers
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "New Movie"
    assert data["duration_minutes"] == 120
    assert "id" in data


def test_create_movie_with_enhanced_fields(client: TestClient, admin_headers):
    """Test creating a movie with all enhanced fields."""
    response = client.post(
        "/api/v1/movies/",
        json={
            "title": "Enhanced Movie",
            "description": "A movie with all fields",
            "duration_minutes": 150,
            "genre": ["Sci-Fi"],
            "rating": "R",
            "cast": ["Actor A", "Actor B", "Actor C"],
            "director": "Famous Director",
            "writers": ["Writer X", "Writer Y"],
            "producers": ["Producer Z"],
            "release_date": "2024-06-15",
            "country": "USA",
            "language": "English",
            "budget": 200000000,
            "revenue": 800000000,
            "production_company": "Big Studio",
            "distributor": "Big Distributor",
            "image_url": "https://example.com/poster.jpg",
            "trailer_url": "https://youtube.com/watch?v=abc123",
            "awards": ["Oscar for Best Picture", "Golden Globe"],
            "details": {"imdb_rating": 8.5, "runtime_extended": 180}
        },
        headers=admin_headers
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Enhanced Movie"
    assert data["cast"] == ["Actor A", "Actor B", "Actor C"]
    assert data["director"] == "Famous Director"
    assert data["budget"] == 200000000
    assert data["image_url"] == "https://example.com/poster.jpg"
    assert data["awards"] == ["Oscar for Best Picture", "Golden Globe"]
    assert data["details"]["imdb_rating"] == 8.5


def test_list_movies(client: TestClient, test_movie):
    """Test listing movies."""
    response = client.get("/api/v1/movies/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert any(m["id"] == test_movie.id for m in data)


def test_get_movie(client: TestClient, test_movie):
    """Test getting a specific movie."""
    response = client.get(f"/api/v1/movies/{test_movie.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_movie.id
    assert data["title"] == test_movie.title
    assert data["cast"] == test_movie.cast
    assert data["director"] == test_movie.director


def test_get_nonexistent_movie(client: TestClient):
    """Test getting a nonexistent movie fails."""
    response = client.get("/api/v1/movies/99999")
    assert response.status_code == 404


def test_update_movie(client: TestClient, test_movie, admin_headers):
    """Test updating a movie."""
    response = client.patch(
        f"/api/v1/movies/{test_movie.id}",
        json={
            "title": "Updated Title",
            "cast": ["New Actor 1", "New Actor 2"],
            "budget": 2000000
        },
        headers=admin_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Title"
    assert data["cast"] == ["New Actor 1", "New Actor 2"]
    assert data["budget"] == 2000000
    # Other fields should remain unchanged
    assert data["genre"] == [test_movie.genre]


def test_update_nonexistent_movie(client: TestClient, admin_headers):
    """Test updating a nonexistent movie fails."""
    response = client.patch(
        "/api/v1/movies/99999",
        json={"title": "Updated"},
        headers=admin_headers
    )
    assert response.status_code == 404


def test_delete_movie(client: TestClient, session, admin_headers):
    """Test deleting a movie."""
    # Create a movie to delete
    from app.models import Movie
    movie = Movie(
        title="To Delete",
        description="Will be deleted",
        duration_minutes=90,
        genre="Horror",
        rating="R"
    )
    session.add(movie)
    session.commit()
    session.refresh(movie)
    movie_id = movie.id
    
    response = client.delete(f"/api/v1/movies/{movie_id}", headers=admin_headers)
    assert response.status_code == 204
    
    # Verify it's deleted
    response = client.get(f"/api/v1/movies/{movie_id}")
    assert response.status_code == 404


def test_delete_nonexistent_movie(client: TestClient, admin_headers):
    """Test deleting a nonexistent movie fails."""
    response = client.delete("/api/v1/movies/99999", headers=admin_headers)
    assert response.status_code == 404


# ============= Search Tests =============

def test_search_movies_by_title(client: TestClient, test_movie, session):
    """Test searching movies by title."""
    response = client.get("/api/v1/movies/search?q=Test")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert any(m["id"] == test_movie.id for m in data)


def test_search_movies_by_genre(client: TestClient, test_movie):
    """Test searching movies by genre."""
    response = client.get(f"/api/v1/movies/search?q={test_movie.genre}")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


def test_search_movies_by_director(client: TestClient, test_movie):
    """Test searching movies by director."""
    response = client.get(f"/api/v1/movies/search?q={test_movie.director}")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert any(m["director"] == test_movie.director for m in data)


def test_search_movies_no_results(client: TestClient):
    """Test searching movies with no results."""
    response = client.get("/api/v1/movies/search?q=NonexistentMovieXYZ123")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 0


def test_search_movies_case_insensitive(client: TestClient, test_movie):
    """Test search is case-insensitive."""
    # Search with lowercase
    response = client.get(f"/api/v1/movies/search?q={test_movie.title.lower()}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    
    # Search with uppercase
    response = client.get(f"/api/v1/movies/search?q={test_movie.title.upper()}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1


# ============= Cast Tests =============

def test_get_movie_cast(client: TestClient, test_movie, session):
    """Test getting movie cast."""
    from app.models import Cast
    # Create test cast members
    cast1 = Cast(
        movie_id=test_movie.id,
        character_name="Character One",
        role="Lead Role",
        actor_name="Actor One",
        order=1
    )
    cast2 = Cast(
        movie_id=test_movie.id,
        character_name="Character Two",
        role="Supporting Role",
        actor_name="Actor Two",
        order=2
    )
    session.add(cast1)
    session.add(cast2)
    session.commit()
    
    response = client.get(f"/api/v1/movies/{test_movie.id}/cast")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 2
    assert data[0]["actor_name"] == "Actor One"
    assert data[1]["actor_name"] == "Actor Two"


def test_get_movie_cast_empty(client: TestClient, session):
    """Test getting cast for movie without cast."""
    from app.models import Movie
    movie = Movie(
        title="No Cast Movie",
        description="Movie without cast",
        duration_minutes=90,
        genre="Drama",
        rating="PG",
        cast=[]
    )
    session.add(movie)
    session.commit()
    session.refresh(movie)
    
    response = client.get(f"/api/v1/movies/{movie.id}/cast")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 0


def test_get_cast_nonexistent_movie(client: TestClient):
    """Test getting cast for nonexistent movie fails."""
    response = client.get("/api/v1/movies/99999/cast")
    assert response.status_code == 404


# ============= Showtimes Tests =============

def test_get_movie_showtimes(client: TestClient, test_movie, test_screening):
    """Test getting movie showtimes."""
    response = client.get(f"/api/v1/movies/{test_movie.id}/showtimes")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    # Verify screening is in the list
    assert any(s["id"] == test_screening.id for s in data)
    # Verify the new structure includes cinema details
    for showtime in data:
        assert "id" in showtime
        assert "screening_time" in showtime
        assert "price" in showtime
        assert "room" in showtime
        assert "cinema" in showtime["room"]
        assert "name" in showtime["room"]["cinema"]
        assert "city" in showtime["room"]["cinema"]


def test_get_movie_showtimes_with_date_filter(client: TestClient, test_movie, test_screening):
    """Test getting movie showtimes filtered by date."""
    from datetime import datetime
    screening_date = test_screening.screening_time.date().isoformat()
    
    response = client.get(f"/api/v1/movies/{test_movie.id}/showtimes?date={screening_date}")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    # Verify structure for date-filtered results
    for showtime in data:
        assert "id" in showtime
        assert "screening_time" in showtime
        assert "price" in showtime
        assert "room" in showtime
        assert "cinema" in showtime["room"]


def test_get_movie_showtimes_filters_past_screenings(client: TestClient, session, test_movie, test_room):
    """Test that past screenings are filtered out."""
    from datetime import datetime, timedelta, timezone
    from app.models import Screening
    
    # Create a past screening
    past_screening = Screening(
        movie_id=test_movie.id,
        room_id=test_room.id,
        screening_time=datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(hours=1),
        price=15.0
    )
    session.add(past_screening)
    session.commit()
    
    response = client.get(f"/api/v1/movies/{test_movie.id}/showtimes")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    # Past screening should not be included
    assert not any(s["id"] == past_screening.id for s in data)
    # Verify all returned screenings are in the future
    current_time = datetime.now(timezone.utc).replace(tzinfo=None)
    for showtime in data:
        screening_time = datetime.fromisoformat(showtime["screening_time"].replace('Z', '+00:00'))
        assert screening_time > current_time


def test_get_movie_showtimes_no_screenings(client: TestClient, session):
    """Test getting showtimes for movie without screenings."""
    from app.models import Movie
    movie = Movie(
        title="No Screenings Movie",
        description="Movie without screenings",
        duration_minutes=90,
        genre="Drama",
        rating="PG"
    )
    session.add(movie)
    session.commit()
    session.refresh(movie)
    
    response = client.get(f"/api/v1/movies/{movie.id}/showtimes")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 0


def test_get_showtimes_nonexistent_movie(client: TestClient):
    """Test getting showtimes for nonexistent movie fails."""
    response = client.get("/api/v1/movies/99999/showtimes")
    assert response.status_code == 404

