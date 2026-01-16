"""User profile routes."""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query
from sqlmodel import Session, select
from typing import Optional, List
import os
from datetime import datetime

from app.config import settings
from app.database import get_session
from app.models.user import User
from app.schemas.user import UserRead, UserUpdate, UserPreferences, UserPreferencesUpdate, UserCreate
from app.services.auth import get_current_active_user, get_current_admin_user, get_password_hash

router = APIRouter(prefix=f"{settings.API_V1_PREFIX}/users", tags=["Users"])


# ============================================================================
# Admin User Management Endpoints
# ============================================================================

@router.get("/admin/users/", response_model=List[UserRead])
def list_all_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by status: active, suspended"),
    role: Optional[str] = Query(None, description="Filter by role: user, admin"),
    session: Session = Depends(get_session),
    current_admin: User = Depends(get_current_admin_user),
):
    """List all users with optional filters (admin only)."""
    query = select(User)
    
    if status_filter:
        if status_filter.lower() == "active":
            query = query.where(User.is_active == True)
        elif status_filter.lower() == "suspended":
            query = query.where(User.is_active == False)
    
    if role:
        if role.lower() == "admin":
            query = query.where(User.is_admin == True)
        elif role.lower() == "user":
            query = query.where(User.is_admin == False)
    
    users = session.exec(query.offset(skip).limit(limit)).all()
    return users


@router.post("/admin/users/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_admin_user(
    user_data: UserCreate,
    session: Session = Depends(get_session),
    current_admin: User = Depends(get_current_admin_user),
):
    """Create a new admin user (admin only)."""
    # Check if email already exists
    existing_user = session.exec(select(User).where(User.email == user_data.email)).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    new_admin = User(
        email=user_data.email,
        full_name=user_data.full_name,
        hashed_password=get_password_hash(user_data.password),
        is_admin=True,
        is_active=True,
    )
    session.add(new_admin)
    session.commit()
    session.refresh(new_admin)
    return new_admin


@router.patch("/admin/users/{user_id}/status", response_model=UserRead)
def update_user_status(
    user_id: int,
    is_active: bool,
    session: Session = Depends(get_session),
    current_admin: User = Depends(get_current_admin_user),
):
    """Update user active/suspended status (admin only)."""
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user.is_active = is_active
    user.updated_at = datetime.utcnow()
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@router.get("/me", response_model=UserRead)
async def get_current_user_profile(current_user: User = Depends(get_current_active_user)):
    """Get current user profile."""
    return current_user


@router.put("/me", response_model=UserRead)
async def update_user_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    """Update current user profile."""
    # Check if email is being updated and if it's already taken
    if user_update.email and user_update.email != current_user.email:
        existing_user = session.exec(
            select(User).where(User.email == user_update.email)
        ).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

    # Update user fields
    update_data = user_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(current_user, field, value)

    current_user.updated_at = datetime.utcnow()
    session.add(current_user)
    session.commit()
    session.refresh(current_user)

    return current_user


@router.put("/me/preferences", response_model=UserPreferences)
async def update_user_preferences(
    preferences: UserPreferencesUpdate,
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    """Update user preferences."""
    update_data = preferences.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(current_user, field, value)

    current_user.updated_at = datetime.utcnow()
    session.add(current_user)
    session.commit()
    session.refresh(current_user)

    return UserPreferences(
        dark_mode=current_user.dark_mode,
        notifications_enabled=current_user.notifications_enabled,
        newsletter_subscribed=current_user.newsletter_subscribed,
    )


@router.put("/me/profile-picture")
async def upload_profile_picture(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    """Upload/update user profile picture."""
    # Validate file type
    allowed_extensions = {".jpg", ".jpeg", ".png", ".gif"}
    file_extension = os.path.splitext(file.filename)[1].lower()

    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only image files (.jpg, .jpeg, .png, .gif) are allowed"
        )

    # Validate file size (max 5MB)
    file_size = 0
    content = await file.read()
    file_size = len(content)

    if file_size > 5 * 1024 * 1024:  # 5MB
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File size must be less than 5MB"
        )

    # Create uploads directory if it doesn't exist
    upload_dir = os.path.join("uploads", "profile_pictures")
    os.makedirs(upload_dir, exist_ok=True)

    # Generate unique filename
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    filename = f"user_{current_user.id}_{timestamp}{file_extension}"
    file_path = os.path.join(upload_dir, filename)

    # Save file
    with open(file_path, "wb") as f:
        f.write(content)

    # Update user profile picture URL
    current_user.profile_picture_url = f"https://localhost:8000/uploads/profile_pictures/{filename}"
    current_user.updated_at = datetime.utcnow()
    session.add(current_user)
    session.commit()
    session.refresh(current_user)

    return {
        "message": "Profile picture uploaded successfully",
        "profile_picture_url": current_user.profile_picture_url
    }


@router.put("/me/profile-picture-url")
async def update_profile_picture_url(
    profile_picture_url: str,
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    """Update user profile picture URL with an absolute URL."""
    # Basic validation for URL format
    if not profile_picture_url.startswith("https://"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Profile picture URL must be an absolute HTTPS URL"
        )

    # Update user profile picture URL
    current_user.profile_picture_url = profile_picture_url
    current_user.updated_at = datetime.utcnow()
    session.add(current_user)
    session.commit()
    session.refresh(current_user)

    return {
        "message": "Profile picture URL updated successfully",
        "profile_picture_url": current_user.profile_picture_url
    }


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_account(
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    """Delete current user account."""
    # Soft delete - mark as inactive instead of hard delete
    current_user.is_active = False
    current_user.updated_at = datetime.utcnow()
    session.add(current_user)
    session.commit()

    return None


@router.get("/{user_id}", response_model=UserRead)
async def get_user_profile(
    user_id: int,
    session: Session = Depends(get_session)
):
    """Get public user profile by ID."""
    user = session.get(User, user_id)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return user