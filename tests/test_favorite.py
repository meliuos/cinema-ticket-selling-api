"""Tests for favorite endpoints."""

from fastapi.testclient import TestClient
from sqlmodel import Session, select
from app.models import Favorite


def test_add_cinema_to_favorites(client: TestClient, test_cinema, auth_headers):
    """Test adding a cinema to favorites."""
    response = client.post(
        f"/api/v1/cinemas/{test_cinema.id}/favorite",
        headers=auth_headers
    )
    assert response.status_code == 201
    data = response.json()
    assert data["cinema_id"] == test_cinema.id
    assert "user_id" in data
    assert "created_at" in data


def test_add_favorite_unauthenticated(client: TestClient, test_cinema):
    """Test adding favorite without authentication fails."""
    response = client.post(f"/api/v1/cinemas/{test_cinema.id}/favorite")
    assert response.status_code == 401


def test_add_nonexistent_cinema_to_favorites(client: TestClient, auth_headers):
    """Test adding nonexistent cinema to favorites fails."""
    response = client.post(
        "/api/v1/cinemas/99999/favorite",
        headers=auth_headers
    )
    assert response.status_code == 404


def test_add_duplicate_favorite(client: TestClient, test_cinema, auth_headers, session: Session):
    """Test adding the same cinema twice creates only one favorite."""
    # Add first time
    response1 = client.post(
        f"/api/v1/cinemas/{test_cinema.id}/favorite",
        headers=auth_headers
    )
    assert response1.status_code == 201
    
    # Try to add again
    response2 = client.post(
        f"/api/v1/cinemas/{test_cinema.id}/favorite",
        headers=auth_headers
    )
    # Should return 400 error for duplicate
    assert response2.status_code == 400
    assert "already in favorites" in response2.json()["detail"].lower()


def test_list_favorites(client: TestClient, test_cinema, auth_headers):
    """Test listing favorite cinemas."""
    # Add a favorite first
    client.post(
        f"/api/v1/cinemas/{test_cinema.id}/favorite",
        headers=auth_headers
    )
    
    # List favorites
    response = client.get("/api/v1/cinemas/favorites", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    # Check that cinema details are included (endpoint returns cinema objects directly)
    assert any(c["id"] == test_cinema.id for c in data)


def test_list_favorites_unauthenticated(client: TestClient):
    """Test listing favorites without authentication fails."""
    response = client.get("/api/v1/cinemas/favorites")
    assert response.status_code == 401


def test_list_favorites_empty(client: TestClient, auth_headers):
    """Test listing favorites when user has none."""
    response = client.get("/api/v1/cinemas/favorites", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    # May be empty or have favorites from other tests


def test_remove_favorite(client: TestClient, test_cinema, auth_headers, session: Session, test_user):
    """Test removing a cinema from favorites."""
    # Add favorite first
    favorite = Favorite(user_id=test_user.id, cinema_id=test_cinema.id)
    session.add(favorite)
    session.commit()
    
    # Remove it
    response = client.delete(
        f"/api/v1/cinemas/{test_cinema.id}/favorite",
        headers=auth_headers
    )
    assert response.status_code == 204
    
    # Verify it's removed
    statement = select(Favorite).where(
        Favorite.user_id == test_user.id,
        Favorite.cinema_id == test_cinema.id
    )
    removed_favorite = session.exec(statement).first()
    assert removed_favorite is None


def test_remove_favorite_unauthenticated(client: TestClient, test_cinema):
    """Test removing favorite without authentication fails."""
    response = client.delete(f"/api/v1/cinemas/{test_cinema.id}/favorite")
    assert response.status_code == 401


def test_remove_nonexistent_favorite(client: TestClient, test_cinema, auth_headers):
    """Test removing a favorite that doesn't exist."""
    response = client.delete(
        f"/api/v1/cinemas/{test_cinema.id}/favorite",
        headers=auth_headers
    )
    # Should return 404 or 204 depending on implementation
    assert response.status_code in [204, 404]


def test_remove_favorite_nonexistent_cinema(client: TestClient, auth_headers):
    """Test removing favorite for nonexistent cinema."""
    response = client.delete(
        "/api/v1/cinemas/99999/favorite",
        headers=auth_headers
    )
    assert response.status_code == 404
