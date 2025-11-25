"""Tests for movie endpoints."""

from fastapi.testclient import TestClient
from datetime import date


def test_create_movie_basic(client: TestClient):
    """Test creating a movie with basic fields."""
    response = client.post(
        "/api/v1/movies/",
        json={
            "title": "New Movie",
            "description": "A new movie",
            "duration_minutes": 120,
            "genre": "Drama",
            "rating": "PG-13"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "New Movie"
    assert data["duration_minutes"] == 120
    assert "id" in data


def test_create_movie_with_enhanced_fields(client: TestClient):
    """Test creating a movie with all enhanced fields."""
    response = client.post(
        "/api/v1/movies/",
        json={
            "title": "Enhanced Movie",
            "description": "A movie with all fields",
            "duration_minutes": 150,
            "genre": "Sci-Fi",
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
        }
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


def test_update_movie(client: TestClient, test_movie):
    """Test updating a movie."""
    response = client.patch(
        f"/api/v1/movies/{test_movie.id}",
        json={
            "title": "Updated Title",
            "cast": ["New Actor 1", "New Actor 2"],
            "budget": 2000000
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Title"
    assert data["cast"] == ["New Actor 1", "New Actor 2"]
    assert data["budget"] == 2000000
    # Other fields should remain unchanged
    assert data["genre"] == test_movie.genre


def test_update_nonexistent_movie(client: TestClient):
    """Test updating a nonexistent movie fails."""
    response = client.patch(
        "/api/v1/movies/99999",
        json={"title": "Updated"}
    )
    assert response.status_code == 404


def test_delete_movie(client: TestClient, session):
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
    
    response = client.delete(f"/api/v1/movies/{movie_id}")
    assert response.status_code == 204
    
    # Verify it's deleted
    response = client.get(f"/api/v1/movies/{movie_id}")
    assert response.status_code == 404


def test_delete_nonexistent_movie(client: TestClient):
    """Test deleting a nonexistent movie fails."""
    response = client.delete("/api/v1/movies/99999")
    assert response.status_code == 404
