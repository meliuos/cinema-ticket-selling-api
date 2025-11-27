"""Tests for authentication endpoints."""

from fastapi.testclient import TestClient
from sqlmodel import Session, select
from datetime import datetime, timedelta, timezone
from app.models.user import User
from app.models.token_blacklist import TokenBlacklist
from app.services.auth import hash_reset_token


def test_register_user(client: TestClient):
    """Test user registration."""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "newuser@example.com",
            "password": "password123",
            "full_name": "New User"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "newuser@example.com"
    assert data["full_name"] == "New User"
    assert "id" in data
    assert "hashed_password" not in data


def test_register_duplicate_email(client: TestClient, test_user):
    """Test registration with existing email fails."""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": test_user.email,
            "password": "password123",
            "full_name": "Duplicate User"
        }
    )
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"].lower()


def test_login(client: TestClient, test_user):
    """Test user login."""
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": test_user.email,
            "password": "testpassword123"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client: TestClient, test_user):
    """Test login with wrong password fails."""
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": test_user.email,
            "password": "wrongpassword"
        }
    )
    assert response.status_code == 401


def test_login_nonexistent_user(client: TestClient):
    """Test login with nonexistent user fails."""
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "nonexistent@example.com",
            "password": "password123"
        }
    )
    assert response.status_code == 401


def test_get_current_user(client: TestClient, test_user, auth_headers):
    """Test getting current user information."""
    response = client.get("/api/v1/auth/me", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == test_user.email
    assert data["full_name"] == test_user.full_name


def test_get_current_user_no_auth(client: TestClient):
    """Test accessing protected endpoint without auth fails."""
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401


# ============= Logout Tests =============

def test_logout_success(client: TestClient, test_user, auth_headers, session: Session):
    """Test successful logout."""
    response = client.post("/api/v1/auth/logout", headers=auth_headers)
    assert response.status_code == 200
    assert "successfully logged out" in response.json()["message"].lower()
    
    # Verify token is blacklisted
    statement = select(TokenBlacklist)
    blacklisted_tokens = session.exec(statement).all()
    assert len(blacklisted_tokens) > 0


def test_logout_no_auth(client: TestClient):
    """Test logout without authentication fails."""
    response = client.post("/api/v1/auth/logout")
    assert response.status_code == 401


def test_logout_token_is_invalidated(client: TestClient, test_user, auth_headers):
    """Test that after logout, the token cannot be used."""
    # Logout
    response = client.post("/api/v1/auth/logout", headers=auth_headers)
    assert response.status_code == 200
    
    # Try to use the same token
    response = client.get("/api/v1/auth/me", headers=auth_headers)
    assert response.status_code == 401
    assert "revoked" in response.json()["detail"].lower()


# ============= Refresh Token Tests =============

def test_refresh_token_success(client: TestClient, test_user, auth_token):
    """Test successful token refresh."""
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = client.post("/api/v1/auth/refresh-token", headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["access_token"] != auth_token  # New token should be different


def test_refresh_token_no_auth(client: TestClient):
    """Test refresh token without authentication fails."""
    response = client.post("/api/v1/auth/refresh-token")
    assert response.status_code == 401


def test_refresh_token_invalid_token(client: TestClient):
    """Test refresh token with invalid token fails."""
    headers = {"Authorization": "Bearer invalid_token_here"}
    response = client.post("/api/v1/auth/refresh-token", headers=headers)
    assert response.status_code == 401


def test_refresh_token_inactive_user(client: TestClient, session: Session, test_user):
    """Test refresh token for inactive user fails."""
    from app.services.auth import create_access_token
    
    # Create token before deactivating user
    token = create_access_token(data={"sub": test_user.email})
    
    # Deactivate user
    test_user.is_active = False
    session.add(test_user)
    session.commit()
    
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post("/api/v1/auth/refresh-token", headers=headers)
    assert response.status_code == 401


def test_refreshed_token_works(client: TestClient, test_user, auth_token):
    """Test that refreshed token can be used for authentication."""
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    # Refresh token
    response = client.post("/api/v1/auth/refresh-token", headers=headers)
    assert response.status_code == 200
    new_token = response.json()["access_token"]
    
    # Use new token to access protected endpoint
    new_headers = {"Authorization": f"Bearer {new_token}"}
    response = client.get("/api/v1/auth/me", headers=new_headers)
    assert response.status_code == 200
    assert response.json()["email"] == test_user.email


# ============= Forgot Password Tests =============

def test_forgot_password_success(client: TestClient, test_user, session: Session):
    """Test successful forgot password request."""
    response = client.post(
        "/api/v1/auth/forgot-password",
        json={"email": test_user.email}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "reset_token" in data
    assert "expires_in_minutes" in data
    assert data["expires_in_minutes"] == 60
    
    # Verify reset token was set in database
    session.refresh(test_user)
    assert test_user.reset_token is not None
    assert test_user.reset_token_expiry is not None
    # Compare with naive datetime since DB stores naive
    assert test_user.reset_token_expiry > datetime.now(timezone.utc).replace(tzinfo=None)


def test_forgot_password_nonexistent_email(client: TestClient):
    """Test forgot password with nonexistent email (should not reveal)."""
    response = client.post(
        "/api/v1/auth/forgot-password",
        json={"email": "nonexistent@example.com"}
    )
    
    # Should return success to prevent email enumeration
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert data["reset_token"] == "not_found"


def test_forgot_password_updates_existing_token(client: TestClient, test_user, session: Session):
    """Test that requesting forgot password again updates the token."""
    # First request
    response1 = client.post(
        "/api/v1/auth/forgot-password",
        json={"email": test_user.email}
    )
    token1 = response1.json()["reset_token"]
    
    # Second request
    response2 = client.post(
        "/api/v1/auth/forgot-password",
        json={"email": test_user.email}
    )
    token2 = response2.json()["reset_token"]
    
    # Tokens should be different
    assert token1 != token2


# ============= Reset Password Tests =============

def test_reset_password_success(client: TestClient, test_user, session: Session):
    """Test successful password reset."""
    # First request a reset token
    response = client.post(
        "/api/v1/auth/forgot-password",
        json={"email": test_user.email}
    )
    reset_token = response.json()["reset_token"]
    
    # Now reset the password
    new_password = "newpassword456"
    response = client.post(
        "/api/v1/auth/reset-password",
        json={
            "token": reset_token,
            "new_password": new_password
        }
    )
    
    assert response.status_code == 200
    assert "successfully reset" in response.json()["message"].lower()
    
    # Verify reset token is cleared
    session.refresh(test_user)
    assert test_user.reset_token is None
    assert test_user.reset_token_expiry is None
    
    # Verify can login with new password
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": test_user.email,
            "password": new_password
        }
    )
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_reset_password_invalid_token(client: TestClient):
    """Test reset password with invalid token fails."""
    response = client.post(
        "/api/v1/auth/reset-password",
        json={
            "token": "invalid_token_here",
            "new_password": "newpassword456"
        }
    )
    
    assert response.status_code == 400
    assert "invalid or expired" in response.json()["detail"].lower()


def test_reset_password_expired_token(client: TestClient, test_user, session: Session):
    """Test reset password with expired token fails."""
    # Set an expired reset token
    from app.services.auth import generate_reset_token
    
    reset_token = generate_reset_token()
    test_user.reset_token = hash_reset_token(reset_token)
    test_user.reset_token_expiry = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(hours=1)  # Expired
    session.add(test_user)
    session.commit()
    
    response = client.post(
        "/api/v1/auth/reset-password",
        json={
            "token": reset_token,
            "new_password": "newpassword456"
        }
    )
    
    assert response.status_code == 400
    assert "invalid or expired" in response.json()["detail"].lower()


def test_reset_password_token_single_use(client: TestClient, test_user, session: Session):
    """Test that reset token can only be used once."""
    # Request reset token
    response = client.post(
        "/api/v1/auth/forgot-password",
        json={"email": test_user.email}
    )
    reset_token = response.json()["reset_token"]
    
    # Use token once
    response = client.post(
        "/api/v1/auth/reset-password",
        json={
            "token": reset_token,
            "new_password": "newpassword456"
        }
    )
    assert response.status_code == 200
    
    # Try to use same token again
    response = client.post(
        "/api/v1/auth/reset-password",
        json={
            "token": reset_token,
            "new_password": "anotherpassword789"
        }
    )
    assert response.status_code == 400
    assert "invalid or expired" in response.json()["detail"].lower()


def test_reset_password_short_password(client: TestClient, test_user):
    """Test reset password with too short password fails."""
    # Request reset token
    response = client.post(
        "/api/v1/auth/forgot-password",
        json={"email": test_user.email}
    )
    reset_token = response.json()["reset_token"]
    
    # Try with short password
    response = client.post(
        "/api/v1/auth/reset-password",
        json={
            "token": reset_token,
            "new_password": "short"  # Less than 8 characters
        }
    )
    
    assert response.status_code == 422  # Validation error


def test_old_password_not_working_after_reset(client: TestClient, test_user):
    """Test that old password doesn't work after reset."""
    old_password = "testpassword123"
    
    # Verify old password works
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": test_user.email,
            "password": old_password
        }
    )
    assert response.status_code == 200
    
    # Request and use reset token
    response = client.post(
        "/api/v1/auth/forgot-password",
        json={"email": test_user.email}
    )
    reset_token = response.json()["reset_token"]
    
    new_password = "newpassword456"
    response = client.post(
        "/api/v1/auth/reset-password",
        json={
            "token": reset_token,
            "new_password": new_password
        }
    )
    assert response.status_code == 200
    
    # Try old password (should fail)
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": test_user.email,
            "password": old_password
        }
    )
    assert response.status_code == 401
    
    # Try new password (should work)
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": test_user.email,
            "password": new_password
        }
    )
    assert response.status_code == 200

