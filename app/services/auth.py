from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
import bcrypt
import secrets
import hashlib
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session, select

from app.config import settings
from app.database import get_session
from app.models.user import User
from app.models.token_blacklist import TokenBlacklist
from app.schemas.user import TokenData

# OAuth2 scheme for token extraction
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_PREFIX}/auth/login")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hashed password."""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))


def get_password_hash(password: str) -> str:
    """Hash a password using bcrypt."""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.
    
    Args:
        data: Data to encode in the token
        expires_delta: Optional expiration time delta
        
    Returns:
        Encoded JWT token string
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # Add JWT ID for token tracking/blacklisting
    jti = secrets.token_urlsafe(32)
    to_encode.update({"exp": expire, "jti": jti})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


async def get_current_user_from_token(token: str, session: Session) -> Optional[User]:
    """
    Get user from JWT token (for WebSocket connections).
    
    Args:
        token: JWT token string
        session: Database session
        
    Returns:
        User object if token is valid, None otherwise
    """
    if not token:
        return None
        
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        jti: str = payload.get("jti")
        
        if email is None or jti is None:
            return None
        
        # Check if token is blacklisted
        if is_token_blacklisted(session, jti):
            return None
        
        # Get user from database
        statement = select(User).where(User.email == email, User.is_active == True)
        user = session.exec(statement).first()
        return user
        
    except JWTError:
        return None


def authenticate_user(session: Session, email: str, password: str) -> Optional[User]:
    """
    Authenticate a user by email and password.
    
    Args:
        session: Database session
        email: User email
        password: Plain password
        
    Returns:
        User object if authentication successful, None otherwise
    """
    statement = select(User).where(User.email == email)
    user = session.exec(statement).first()
    
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def is_token_blacklisted(session: Session, jti: str) -> bool:
    """
    Check if a token is blacklisted.
    
    Args:
        session: Database session
        jti: JWT ID (jti claim)
        
    Returns:
        True if token is blacklisted, False otherwise
    """
    statement = select(TokenBlacklist).where(TokenBlacklist.token_jti == jti)
    blacklisted = session.exec(statement).first()
    return blacklisted is not None


def blacklist_token(session: Session, jti: str, user_id: int, expires_at: datetime) -> None:
    """
    Add a token to the blacklist.
    
    Args:
        session: Database session
        jti: JWT ID (jti claim)
        user_id: User ID
        expires_at: Token expiration time
    """
    blacklist_entry = TokenBlacklist(
        token_jti=jti,
        user_id=user_id,
        expires_at=expires_at
    )
    session.add(blacklist_entry)
    session.commit()


def generate_reset_token() -> str:
    """
    Generate a secure random token for password reset.
    
    Returns:
        A URL-safe random token
    """
    return secrets.token_urlsafe(32)


def hash_reset_token(token: str) -> str:
    """
    Hash a reset token for secure storage.
    
    Args:
        token: Plain reset token
        
    Returns:
        SHA256 hash of the token
    """
    return hashlib.sha256(token.encode()).hexdigest()


def verify_reset_token(session: Session, token: str) -> Optional[User]:
    """
    Verify a password reset token and return the associated user.
    
    Args:
        session: Database session
        token: Plain reset token
        
    Returns:
        User if token is valid and not expired, None otherwise
    """
    hashed_token = hash_reset_token(token)
    statement = select(User).where(
        User.reset_token == hashed_token,
        User.reset_token_expiry > datetime.now(timezone.utc)
    )
    user = session.exec(statement).first()
    return user


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: Session = Depends(get_session)
) -> User:
    """
    Get the current user from the JWT token.
    
    Args:
        token: JWT token from Authorization header
        session: Database session
        
    Returns:
        Current user object
        
    Raises:
        HTTPException: If token is invalid or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        jti: str = payload.get("jti")
        
        if email is None or jti is None:
            raise credentials_exception
        
        # Check if token is blacklisted
        if is_token_blacklisted(session, jti):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has been revoked",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        token_data = TokenData(email=email)
    except JWTError:
        raise credentials_exception
    
    statement = select(User).where(User.email == token_data.email)
    user = session.exec(statement).first()
    
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """
    Get the current active user.
    
    Args:
        current_user: Current user from token
        
    Returns:
        Current user if active
        
    Raises:
        HTTPException: If user is inactive
    """
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


async def get_current_admin_user(current_user: User = Depends(get_current_active_user)) -> User:
    """
    Get the current admin user.
    
    Args:
        current_user: Current active user from token
        
    Returns:
        Current user if they are an admin
        
    Raises:
        HTTPException: If user is not an admin
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions. Admin access required."
        )
    return current_user
