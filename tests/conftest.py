"""Test configuration and fixtures."""

import pytest
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool
from fastapi.testclient import TestClient

from app.main import app
from app.database import get_session
from app.models import User, Cinema, Room, Seat, Movie, Screening, Ticket
from app.services.auth import get_password_hash, create_access_token


@pytest.fixture(name="session")
def session_fixture():
    """Create a test database session."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    """Create a test client with overridden database session."""
    def get_session_override():
        return session
    
    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture(name="test_user")
def test_user_fixture(session: Session):
    """Create a test user."""
    user = User(
        email="test@example.com",
        full_name="Test User",
        hashed_password=get_password_hash("testpassword123"),
        is_active=True
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@pytest.fixture(name="auth_token")
def auth_token_fixture(test_user: User):
    """Create an authentication token for the test user."""
    token = create_access_token(data={"sub": test_user.email})
    return token


@pytest.fixture(name="auth_headers")
def auth_headers_fixture(auth_token: str):
    """Create authentication headers."""
    return {"Authorization": f"Bearer {auth_token}"}


@pytest.fixture(name="test_cinema")
def test_cinema_fixture(session: Session):
    """Create a test cinema."""
    cinema = Cinema(
        name="Test Cinema",
        address="123 Test Street",
        city="Test City"
    )
    session.add(cinema)
    session.commit()
    session.refresh(cinema)
    return cinema


@pytest.fixture(name="test_room")
def test_room_fixture(session: Session, test_cinema: Cinema):
    """Create a test room."""
    room = Room(
        name="Test Room",
        cinema_id=test_cinema.id
    )
    session.add(room)
    session.commit()
    session.refresh(room)
    return room


@pytest.fixture(name="test_seats")
def test_seats_fixture(session: Session, test_room: Room):
    """Create test seats."""
    seats = []
    for row in ["A", "B"]:
        for num in range(1, 6):  # 5 seats per row
            seat = Seat(
                room_id=test_room.id,
                row_label=row,
                seat_number=num,
                seat_type="standard"
            )
            session.add(seat)
            seats.append(seat)
    session.commit()
    for seat in seats:
        session.refresh(seat)
    return seats


@pytest.fixture(name="test_movie")
def test_movie_fixture(session: Session):
    """Create a test movie with enhanced fields."""
    from datetime import date
    movie = Movie(
        title="Test Movie",
        description="A test movie description",
        duration_minutes=120,
        genre="Action",
        rating="PG-13",
        cast=["Actor One", "Actor Two"],
        director="Test Director",
        writers=["Writer One"],
        release_date=date(2024, 1, 1),
        country="USA",
        language="English",
        budget=1000000,
        revenue=5000000,
        production_company="Test Productions",
        image_url="https://example.com/image.jpg",
        trailer_url="https://example.com/trailer.mp4",
        awards=["Best Test Movie"],
        details={"test_field": "test_value"}
    )
    session.add(movie)
    session.commit()
    session.refresh(movie)
    return movie


@pytest.fixture(name="test_screening")
def test_screening_fixture(session: Session, test_movie: Movie, test_room: Room):
    """Create a test screening."""
    from datetime import datetime, timedelta
    screening = Screening(
        movie_id=test_movie.id,
        room_id=test_room.id,
        screening_time=datetime.utcnow() + timedelta(days=1),
        price=15.0
    )
    session.add(screening)
    session.commit()
    session.refresh(screening)
    return screening
