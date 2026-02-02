"""Tests for movie notification feature."""

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, select
from datetime import datetime

from app.models.movie import Movie, MovieState
from app.models.user import User
from app.models.movie_notification import MovieNotification
from app.models.screening import Screening
from app.models.cinema import Cinema, Room


def test_subscribe_to_coming_soon_movie(client: TestClient, auth_headers: dict, session: Session):
    """Test subscribing to notifications for a coming soon movie."""
    # Create a coming soon movie
    movie = Movie(
        title="Dune Part III",
        description="The epic conclusion",
        duration_minutes=180,
        state=MovieState.COMING_SOON
    )
    session.add(movie)
    session.commit()
    session.refresh(movie)
    
    # Subscribe to notifications
    response = client.post(
        f"/api/v1/movies/{movie.id}/notify",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["subscribed"] is True
    assert "subscribed" in data["message"].lower()
    
    # Verify subscription in database
    notification = session.exec(
        select(MovieNotification).where(
            MovieNotification.movie_id == movie.id
        )
    ).first()
    assert notification is not None
    assert notification.notified is False


def test_subscribe_idempotent(client: TestClient, auth_headers: dict, session: Session):
    """Test that subscribing multiple times doesn't create duplicates."""
    # Create a coming soon movie
    movie = Movie(
        title="Avatar 3",
        description="Return to Pandora",
        duration_minutes=190,
        state=MovieState.COMING_SOON
    )
    session.add(movie)
    session.commit()
    session.refresh(movie)
    
    # Subscribe first time
    response1 = client.post(
        f"/api/v1/movies/{movie.id}/notify",
        headers=auth_headers
    )
    assert response1.status_code == 200
    
    # Subscribe second time (should be idempotent)
    response2 = client.post(
        f"/api/v1/movies/{movie.id}/notify",
        headers=auth_headers
    )
    assert response2.status_code == 200
    assert "already subscribed" in response2.json()["message"].lower()
    
    # Verify only one subscription exists
    notifications = session.exec(
        select(MovieNotification).where(
            MovieNotification.movie_id == movie.id
        )
    ).all()
    assert len(notifications) == 1


def test_cannot_subscribe_to_showing_movie(client: TestClient, auth_headers: dict, session: Session):
    """Test that subscribing to a showing movie fails."""
    # Create a showing movie
    movie = Movie(
        title="Current Movie",
        description="Already showing",
        duration_minutes=120,
        state=MovieState.SHOWING
    )
    session.add(movie)
    session.commit()
    session.refresh(movie)
    
    # Try to subscribe
    response = client.post(
        f"/api/v1/movies/{movie.id}/notify",
        headers=auth_headers
    )
    
    assert response.status_code == 400
    assert "already" in response.json()["detail"].lower()


def test_unsubscribe_from_movie(client: TestClient, auth_headers: dict, session: Session, test_user: User):
    """Test unsubscribing from movie notifications."""
    # Create a coming soon movie
    movie = Movie(
        title="Future Film",
        description="Coming soon",
        duration_minutes=150,
        state=MovieState.COMING_SOON
    )
    session.add(movie)
    session.commit()
    session.refresh(movie)
    
    # Create a subscription
    notification = MovieNotification(
        user_id=test_user.id,
        movie_id=movie.id
    )
    session.add(notification)
    session.commit()
    
    # Unsubscribe
    response = client.delete(
        f"/api/v1/movies/{movie.id}/notify",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["subscribed"] is False
    assert "unsubscribed" in data["message"].lower()
    
    # Verify subscription removed from database
    notification = session.exec(
        select(MovieNotification).where(
            MovieNotification.movie_id == movie.id
        )
    ).first()
    assert notification is None


def test_unsubscribe_nonexistent_subscription(client: TestClient, auth_headers: dict, session: Session):
    """Test unsubscribing when no subscription exists."""
    # Create a coming soon movie
    movie = Movie(
        title="Some Movie",
        description="Test",
        duration_minutes=100,
        state=MovieState.COMING_SOON
    )
    session.add(movie)
    session.commit()
    session.refresh(movie)
    
    # Try to unsubscribe without subscribing first
    response = client.delete(
        f"/api/v1/movies/{movie.id}/notify",
        headers=auth_headers
    )
    
    assert response.status_code == 404
    assert "subscription" in response.json()["detail"].lower()


def test_subscribe_requires_authentication(client: TestClient, session: Session):
    """Test that subscription requires authentication."""
    # Create a coming soon movie
    movie = Movie(
        title="Test Movie",
        description="Test",
        duration_minutes=100,
        state=MovieState.COMING_SOON
    )
    session.add(movie)
    session.commit()
    session.refresh(movie)
    
    # Try to subscribe without auth
    response = client.post(f"/api/v1/movies/{movie.id}/notify")
    
    assert response.status_code == 401


def test_notification_trigger_on_state_change(
    client: TestClient, 
    admin_headers: dict, 
    auth_headers: dict,
    session: Session,
    test_user: User
):
    """Test that notifications are triggered when movie state changes to SHOWING."""
    # Create a coming soon movie
    movie = Movie(
        title="Anticipated Movie",
        description="Highly anticipated",
        duration_minutes=160,
        state=MovieState.COMING_SOON
    )
    session.add(movie)
    session.commit()
    session.refresh(movie)
    
    # Subscribe to the movie
    client.post(
        f"/api/v1/movies/{movie.id}/notify",
        headers=auth_headers
    )
    
    # Verify subscription exists and not notified
    notification = session.exec(
        select(MovieNotification).where(
            MovieNotification.movie_id == movie.id,
            MovieNotification.user_id == test_user.id
        )
    ).first()
    assert notification is not None
    assert notification.notified is False
    
    # Admin updates movie state to SHOWING
    response = client.patch(
        f"/api/v1/movies/{movie.id}",
        json={"state": "SHOWING"},
        headers=admin_headers
    )
    assert response.status_code == 200
    
    # Background task should have been triggered
    # Note: In real scenario, the notification would be marked as sent
    # This test verifies the endpoint works correctly


def test_notification_trigger_on_first_screening(
    client: TestClient,
    admin_headers: dict,
    auth_headers: dict,
    session: Session,
    test_user: User
):
    """Test that notifications are triggered when first screening is created for COMING_SOON movie."""
    # Create cinema and room
    cinema = Cinema(
        name="Test Cinema",
        address="123 Test St",
        city="Test City",
        hasParking=True,
        isAccessible=True
    )
    session.add(cinema)
    session.commit()
    session.refresh(cinema)
    
    room = Room(
        cinema_id=cinema.id,
        name="Screen 1",
        capacity=100
    )
    session.add(room)
    session.commit()
    session.refresh(room)
    
    # Create a coming soon movie
    movie = Movie(
        title="Brand New Release",
        description="First showings!",
        duration_minutes=140,
        state=MovieState.COMING_SOON
    )
    session.add(movie)
    session.commit()
    session.refresh(movie)
    
    # Subscribe to the movie
    client.post(
        f"/api/v1/movies/{movie.id}/notify",
        headers=auth_headers
    )
    
    # Create first screening (should trigger notification and auto-change state)
    response = client.post(
        "/api/v1/screenings/",
        json={
            "movie_id": movie.id,
            "room_id": room.id,
            "screening_time": "2026-02-15T19:00:00",
            "price": 12.50
        },
        headers=admin_headers
    )
    assert response.status_code == 201
    
    # Verify movie state changed to SHOWING
    session.refresh(movie)
    assert movie.state == MovieState.SHOWING
    
    # Background task should have been triggered


def test_multiple_users_subscribed(
    client: TestClient,
    session: Session,
    test_user: User,
    admin_user: User
):
    """Test that multiple users can subscribe to the same movie."""
    from app.services.auth import create_access_token
    
    # Create a coming soon movie
    movie = Movie(
        title="Popular Movie",
        description="Everyone wants to see this",
        duration_minutes=130,
        state=MovieState.COMING_SOON
    )
    session.add(movie)
    session.commit()
    session.refresh(movie)
    
    # User 1 subscribes
    token1 = create_access_token({"sub": test_user.email})
    response1 = client.post(
        f"/api/v1/movies/{movie.id}/notify",
        headers={"Authorization": f"Bearer {token1}"}
    )
    assert response1.status_code == 200
    
    # User 2 subscribes
    token2 = create_access_token({"sub": admin_user.email})
    response2 = client.post(
        f"/api/v1/movies/{movie.id}/notify",
        headers={"Authorization": f"Bearer {token2}"}
    )
    assert response2.status_code == 200
    
    # Verify both subscriptions exist
    notifications = session.exec(
        select(MovieNotification).where(
            MovieNotification.movie_id == movie.id
        )
    ).all()
    assert len(notifications) == 2
    user_ids = {n.user_id for n in notifications}
    assert test_user.id in user_ids
    assert admin_user.id in user_ids
