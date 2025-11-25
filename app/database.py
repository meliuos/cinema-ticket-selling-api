from sqlmodel import SQLModel, create_engine, Session
from app.config import settings
from app.models import User, Cinema, Room, Seat, Movie, Screening, Ticket  # noqa: F401

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
    with Session(engine) as session:
        yield session
