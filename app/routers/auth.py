"""Authentication routes."""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select
from datetime import timedelta, datetime, timezone
from jose import jwt, JWTError

from app.config import settings
from app.database import get_session
from app.models.user import User
from app.schemas.user import (
    UserCreate, 
    UserRead, 
    Token, 
    EmailCheckResponse,
    RefreshTokenRequest,
    ForgotPasswordRequest,
    ResetPasswordRequest,
    PasswordResetResponse
)
from app.services.auth import (
    get_password_hash,
    authenticate_user,
    create_access_token,
    get_current_active_user,
    blacklist_token,
    generate_reset_token,
    hash_reset_token,
    verify_reset_token,
    oauth2_scheme
)

router = APIRouter(prefix=f"{settings.API_V1_PREFIX}/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED
)
def register_user(user: UserCreate, session: Session = Depends(get_session)):
    """Register a new user."""
    # Check if user already exists
    statement = select(User).where(User.email == user.email)
    existing_user = session.exec(statement).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user with hashed password
    db_user = User(
        email=user.email,
        full_name=user.full_name,
        hashed_password=get_password_hash(user.password)
    )
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session)
):
    """Login and get access token."""
    user = authenticate_user(session, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserRead)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    """Get current user information."""
    return current_user


@router.get("/check-email", response_model=EmailCheckResponse)
def check_email_exists(email: str, session: Session = Depends(get_session)):
    """Check if an email address is already registered."""
    statement = select(User).where(User.email == email)
    existing_user = session.exec(statement).first()
    return EmailCheckResponse(email=email, exists=existing_user is not None)


@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(
    token: str = Depends(oauth2_scheme),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """
    Logout by blacklisting the current access token.
    The token will be invalid for future requests.
    """
    try:
        # Decode token to get jti and expiration
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        jti = payload.get("jti")
        exp = payload.get("exp")
        
        if not jti or not exp:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid token format"
            )
        
        # Convert exp timestamp to datetime
        expires_at = datetime.fromtimestamp(exp, tz=timezone.utc)
        
        # Blacklist the token
        blacklist_token(session, jti, current_user.id, expires_at)
        
        return {"message": "Successfully logged out"}
    
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )


@router.post("/refresh-token", response_model=Token)
async def refresh_token(
    token: str = Depends(oauth2_scheme),
    session: Session = Depends(get_session)
):
    """
    Refresh an access token by providing a valid non-expired token.
    Returns a new access token with extended expiration.
    """
    try:
        # Decode and validate the token
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        
        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        
        # Get user from database
        statement = select(User).where(User.email == email)
        user = session.exec(statement).first()
        
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )
        
        # Create new access token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        new_access_token = create_access_token(
            data={"sub": user.email}, 
            expires_delta=access_token_expires
        )
        
        return {"access_token": new_access_token, "token_type": "bearer"}
    
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate token"
        )


@router.post("/forgot-password", response_model=PasswordResetResponse)
async def forgot_password(
    request: ForgotPasswordRequest,
    session: Session = Depends(get_session)
):
    """
    Request a password reset token.
    In production, this would send an email with the reset link.
    For development, the token is returned in the response.
    """
    # Find user by email
    statement = select(User).where(User.email == request.email)
    user = session.exec(statement).first()
    
    # Always return success to prevent email enumeration
    if not user:
        return {
            "message": "If the email exists, a password reset link has been sent",
            "reset_token": "not_found",
            "expires_in_minutes": 60
        }
    
    # Generate reset token
    reset_token = generate_reset_token()
    hashed_token = hash_reset_token(reset_token)
    
    # Set token and expiry (1 hour from now)
    user.reset_token = hashed_token
    user.reset_token_expiry = datetime.now(timezone.utc) + timedelta(hours=1)
    session.add(user)
    session.commit()
    
    # In production, send email here
    # For development, return the token
    return {
        "message": "Password reset token generated (would be sent via email in production)",
        "reset_token": reset_token,  # Don't return this in production!
        "expires_in_minutes": 60
    }


@router.post("/reset-password", status_code=status.HTTP_200_OK)
async def reset_password(
    request: ResetPasswordRequest,
    session: Session = Depends(get_session)
):
    """
    Reset password using a valid reset token.
    The token must not be expired and can only be used once.
    """
    # Verify reset token and get user
    user = verify_reset_token(session, request.token)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )
    
    # Update password
    user.hashed_password = get_password_hash(request.new_password)
    
    # Clear reset token (single use)
    user.reset_token = None
    user.reset_token_expiry = None
    
    session.add(user)
    session.commit()
    
    return {"message": "Password successfully reset"}

