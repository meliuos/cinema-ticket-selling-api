"""Tests for admin dashboard endpoints."""

from fastapi.testclient import TestClient


def test_get_movies_count_admin(client: TestClient, admin_headers):
    """Test getting movies count as admin."""
    response = client.get("/api/v1/admin/stats/movies", headers=admin_headers)
    assert response.status_code == 200

    data = response.json()
    assert "movies_count" in data
    assert isinstance(data["movies_count"], int)
    assert data["movies_count"] >= 0


def test_get_cinemas_count_admin(client: TestClient, admin_headers):
    """Test getting cinemas count as admin."""
    response = client.get("/api/v1/admin/stats/cinemas", headers=admin_headers)
    assert response.status_code == 200

    data = response.json()
    assert "cinemas_count" in data
    assert isinstance(data["cinemas_count"], int)
    assert data["cinemas_count"] >= 0


def test_get_users_count_admin(client: TestClient, admin_headers):
    """Test getting users count as admin."""
    response = client.get("/api/v1/admin/stats/users", headers=admin_headers)
    assert response.status_code == 200

    data = response.json()
    assert "users_count" in data
    assert isinstance(data["users_count"], int)
    assert data["users_count"] >= 0


def test_get_recent_bookings_admin(client: TestClient, admin_headers, test_screening, test_seats):
    """Test getting recent bookings as admin."""
    # Create a booking first to have recent bookings
    client.post(
        "/api/v1/tickets/book",
        headers=admin_headers,
        json={
            "screening_id": test_screening.id,
            "seat_ids": [test_seats[0].id]
        }
    )

    response = client.get("/api/v1/admin/stats/bookings/recent", headers=admin_headers)
    assert response.status_code == 200

    data = response.json()
    assert "recent_bookings" in data
    assert isinstance(data["recent_bookings"], list)

    if data["recent_bookings"]:
        booking = data["recent_bookings"][0]
        assert "id" in booking
        assert "user_id" in booking
        assert "screening_id" in booking
        assert "seat_id" in booking
        assert "price" in booking
        assert "status" in booking
        assert "booked_at" in booking


def test_get_total_revenue_admin(client: TestClient, admin_headers):
    """Test getting total revenue as admin."""
    response = client.get("/api/v1/admin/stats/revenue", headers=admin_headers)
    assert response.status_code == 200

    data = response.json()
    assert "total_revenue" in data
    assert isinstance(data["total_revenue"], (int, float))
    assert data["total_revenue"] >= 0


def test_get_revenue_by_period_admin(client: TestClient, admin_headers):
    """Test getting revenue by period as admin."""
    response = client.get("/api/v1/admin/stats/revenue/period", headers=admin_headers)
    assert response.status_code == 200

    data = response.json()
    assert "revenue_last_period" in data
    assert "period_days" in data
    assert isinstance(data["revenue_last_period"], (int, float))
    assert data["period_days"] == 30


def test_get_total_tickets_sold_admin(client: TestClient, admin_headers):
    """Test getting total tickets sold as admin."""
    response = client.get("/api/v1/admin/stats/tickets/total", headers=admin_headers)
    assert response.status_code == 200

    data = response.json()
    assert "total_tickets_sold" in data
    assert isinstance(data["total_tickets_sold"], int)
    assert data["total_tickets_sold"] >= 0


def test_get_popular_movies_admin(client: TestClient, admin_headers):
    """Test getting popular movies as admin."""
    response = client.get("/api/v1/admin/stats/movies/popular", headers=admin_headers)
    assert response.status_code == 200

    data = response.json()
    assert "popular_movies" in data
    assert isinstance(data["popular_movies"], list)


def test_get_today_stats_admin(client: TestClient, admin_headers):
    """Test getting today's statistics as admin."""
    response = client.get("/api/v1/admin/stats/today", headers=admin_headers)
    assert response.status_code == 200

    data = response.json()
    assert "today_bookings" in data
    assert "today_revenue" in data
    assert "date" in data
    assert isinstance(data["today_bookings"], int)
    assert isinstance(data["today_revenue"], (int, float))


def test_admin_stats_no_auth(client: TestClient):
    """Test admin stats endpoints without authentication fails."""
    endpoints = [
        "/api/v1/admin/stats/movies",
        "/api/v1/admin/stats/cinemas",
        "/api/v1/admin/stats/users",
        "/api/v1/admin/stats/bookings/recent",
        "/api/v1/admin/stats/revenue",
        "/api/v1/admin/stats/revenue/period",
        "/api/v1/admin/stats/tickets/total",
        "/api/v1/admin/stats/movies/popular",
        "/api/v1/admin/stats/today"
    ]

    for endpoint in endpoints:
        response = client.get(endpoint)
        assert response.status_code == 401


def test_admin_stats_regular_user(client: TestClient, auth_headers):
    """Test admin stats endpoints as regular user fails."""
    endpoints = [
        "/api/v1/admin/stats/movies",
        "/api/v1/admin/stats/cinemas",
        "/api/v1/admin/stats/users",
        "/api/v1/admin/stats/bookings/recent",
        "/api/v1/admin/stats/revenue",
        "/api/v1/admin/stats/revenue/period",
        "/api/v1/admin/stats/tickets/total",
        "/api/v1/admin/stats/movies/popular",
        "/api/v1/admin/stats/today"
    ]

    for endpoint in endpoints:
        response = client.get(endpoint, headers=auth_headers)
        assert response.status_code == 403