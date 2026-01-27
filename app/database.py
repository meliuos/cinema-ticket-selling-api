from sqlmodel import SQLModel, create_engine, Session
from app.config import settings
from app.models import (
    User, Cinema, Room, Seat, Movie, Screening, Ticket, Review, Favorite, SearchHistory, TokenBlacklist
)
import logging

logger = logging.getLogger(__name__)  

# Create database engine
engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,  # Log SQL queries in debug mode
    pool_pre_ping=True,   # Verify connections before using them
)


def create_db_and_tables():
    """Create database tables based on SQLModel models."""
    SQLModel.metadata.create_all(engine)


def get_session():
    """Dependency to get database session."""
    logger.info(f"[SESSION] Creating new session")
    with Session(engine) as session:
        logger.info(f"[SESSION] Session created. State: in_transaction={session.in_transaction()}, is_active={session.is_active}")
        try:
            yield session
            logger.info(f"[SESSION] After yield (before context exit). State: in_transaction={session.in_transaction()}, is_active={session.is_active}")
        except Exception as e:
            logger.error(f"[SESSION] Exception during request: {type(e).__name__}: {e}")
            raise
        finally:
            logger.info(f"[SESSION] In finally block (about to exit context). State: in_transaction={session.in_transaction()}, is_active={session.is_active}")
    logger.info(f"[SESSION] After context exit")
