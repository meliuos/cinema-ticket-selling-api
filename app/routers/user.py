"""User profile routes."""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlmodel import Session, select
from typing import Optional
import os
from datetime import datetime

from app.config import settings
from app.database import get_session
from app.models.user import User
from app.schemas.user import UserRead, UserUpdate, UserPreferences, UserPreferencesUpdate
from app.services.auth import get_current_active_user

router = APIRouter(prefix=f"{settings.API_V1_PREFIX}/users", tags=["Users"])


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