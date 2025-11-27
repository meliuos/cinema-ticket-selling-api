# Cinema Ticketing API - FastAPI Backend

A complete cinema ticket booking system built with FastAPI, SQLModel ORM, JWT authentication, and PostgreSQL.

## 🎬 Features

- **Cinema Management**: Cinemas, rooms, and seat configuration
- **Movie Catalog**: Movie information with genres and ratings
- **Screenings**: Schedule movies across different rooms and times
- **Ticket Booking**: Secure ticket purchases with JWT authentication
- **Real-time Availability**: Live seat availability tracking
- **User Management**: Registration, login, and profile management

## 🛠️ Tech Stack

- **FastAPI** - Modern Python API framework
- **SQLModel** - SQL ORM with Pydantic validation
- **PostgreSQL** - Relational database
- **JWT** - Token-based authentication
- **Bcrypt** - Secure password hashing

## 📁 Project Structure

```
fastapi/
├── app/
│   ├── __init__.py
│   ├── main.py             # FastAPI app & all endpoints
│   ├── config.py           # Settings & environment config
│   ├── database.py         # Database connection
│   ├── models.py           # SQLModel models & schemas
│   ├── auth.py             # Authentication utilities
│   └── cinema_service.py   # Business logic layer
├── seed.py                 # Database seeding script
├── start.sh                # Quick start script
├── .env                    # Environment variables
├── .env.example            # Environment template
├── requirements.txt        # Python dependencies
└── README.md
```

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- PostgreSQL 12+

### 1. Clone & Setup Virtual Environment

```bash
cd /home/mootez/Desktop/fastapi

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your PostgreSQL credentials
# Important: Update DATABASE_URL with your password
```

### 4. Create Database

```bash
# Using psql
psql -U postgres -c "CREATE DATABASE fastapi_db;"

# Or using your PostgreSQL client
```

### 5. Start the Server

**Option A: Quick Start (with seeding)**

```bash
./start.sh --seed
```

**Option B: Quick Start (without seeding)**

```bash
./start.sh
```

**Option C: Manual Start**

```bash
# Without seeding
venv/bin/uvicorn app.main:app --reload

# With seeding (first time only)
venv/bin/python seed.py
venv/bin/uvicorn app.main:app --reload
```

The API will be running at: **http://localhost:8000**

## 📚 Database Setup

### Database Migrations with Alembic

This project uses **Alembic** for database migrations to manage schema changes safely across environments.

#### Initial Setup

```bash
# 1. Install dependencies (Alembic already included in requirements.txt)
pip install -r requirements.txt

# 2. Apply all existing migrations to your database
alembic upgrade head

# 3. Seed the database with sample data (if needed)
python seed.py
```

#### Creating New Migrations

When you modify any SQLModel classes (add/remove/change fields), create a migration:

```bash
# Generate migration automatically
alembic revision --autogenerate -m "Describe your changes"

# Review the generated migration file in alembic/versions/
# Make manual adjustments if needed

# Apply the migration
alembic upgrade head
```

#### Common Alembic Commands

```bash
# Check current migration status
alembic current

# View migration history
alembic history --verbose

# Upgrade to specific revision
alembic upgrade <revision_id>

# Downgrade to previous migration
alembic downgrade -1

# Downgrade to specific revision
alembic downgrade <revision_id>

# Create empty migration (for manual changes)
alembic revision -m "Description"
```

### Database Seeding

The `seed.py` script populates the database with sample data:

```bash
venv/bin/python seed.py
```

**Sample Data Includes**:

- 2 Cinemas (Tunis locations)
- 3 Rooms (including IMAX)
- 300+ Seats (auto-configured)
- 5 Movies (Matrix, Inception, Dark Knight, etc.)
- 80+ Screenings (next 7 days)
- 1 Demo user (`demo@cinema.com` / `demo123`)

> **Note**: Seeding is idempotent - it won't duplicate data if run multiple times.

### Manual Database Reset

```bash
# Drop and recreate database
psql -U postgres -c "DROP DATABASE fastapi_db;"
psql -U postgres -c "CREATE DATABASE fastapi_db;"

# Restart server (tables auto-created)
venv/bin/uvicorn app.main:app --reload

# Re-seed data
venv/bin/python seed.py
```

## 📖 API Documentation

Interactive API documentation is automatically available:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🔗 API Endpoints Overview

### Authentication

- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login (get JWT token)
- `GET /api/v1/auth/me` - Get current user info 🔐

### Cinemas

- `POST /api/v1/cinemas/` - Create cinema
- `GET /api/v1/cinemas/` - List cinemas
- `GET /api/v1/cinemas/{id}` - Get cinema details

### Rooms

- `POST /api/v1/cinemas/{cinema_id}/rooms/` - Create room
- `GET /api/v1/cinemas/{cinema_id}/rooms/` - List rooms
- `GET /api/v1/rooms/{id}` - Get room details

### Seats

- `POST /api/v1/rooms/{room_id}/seats/bulk` - Bulk create seats
- `GET /api/v1/rooms/{room_id}/seats/` - List seats

### Movies

- `POST /api/v1/movies/` - Create movie
- `GET /api/v1/movies/` - List movies
- `GET /api/v1/movies/{id}` - Get movie details

### Screenings

- `POST /api/v1/screenings/` - Create screening
- `GET /api/v1/screenings/` - List screenings (filterable)
- `GET /api/v1/screenings/{id}` - Get screening details
- `GET /api/v1/screenings/{id}/available-seats` - Get available seats

### Tickets (Protected 🔐)

- `POST /api/v1/tickets/book` - Book tickets
- `GET /api/v1/tickets/my-tickets` - Get user's tickets
- `GET /api/v1/tickets/{id}` - Get ticket details
- `DELETE /api/v1/tickets/{id}` - Cancel ticket

> 🔐 = Requires JWT authentication (Bearer token)

## 🧪 Quick Test

### 1. Register a User

```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123",
    "full_name": "Test User"
  }'
```

### 2. Login & Get Token

```bash
TOKEN=$(curl -s -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=test@example.com&password=password123" \
  | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

echo $TOKEN
```

### 3. Book Tickets

```bash
curl -X POST "http://localhost:8000/api/v1/tickets/book" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "screening_id": 1,
    "seat_ids": [1, 2, 3]
  }'
```

### 4. Get Your Tickets

```bash
curl "http://localhost:8000/api/v1/tickets/my-tickets" \
  -H "Authorization: Bearer $TOKEN"
```

## ⚙️ Configuration

Environment variables in `.env`:

```env
# Database
DATABASE_URL=postgresql://postgres:your_password@localhost:5432/fastapi_db

# Application
APP_NAME=Cinema Ticketing API
DEBUG=True
API_V1_PREFIX=/api/v1

# Authentication (generate with: openssl rand -hex 32)
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=43200  # 30 days
```

## 🔧 Development Commands

```bash
# Activate virtual environment
source venv/bin/activate

# Install new dependencies
pip install <package-name>
pip freeze > requirements.txt

# Run server with auto-reload
venv/bin/uvicorn app.main:app --reload

# Run server on different port
venv/bin/uvicorn app.main:app --reload --port 8080

# Seed database
venv/bin/python seed.py

# Python shell with models
venv/bin/python
>>> from app.models import *
>>> from app.database import *
```

## 📦 Dependencies

**Core**:

- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `sqlmodel` - ORM
- `psycopg2-binary` - PostgreSQL adapter
- `pydantic` - Data validation

**Security**:

- `python-jose[cryptography]` - JWT tokens
- `bcrypt` - Password hashing
- `python-multipart` - Form data

**Configuration**:

- `python-dotenv` - Environment variables
- `pydantic-settings` - Settings management

## 🎯 Next Steps

- [x] Add Alembic for database migrations
- [ ] Implement refresh tokens
- [ ] Add email verification
- [ ] Create admin panel
- [ ] Add payment integration
- [ ] Implement seat selection UI
- [ ] Add booking notifications
- [ ] Set up testing with pytest
- [ ] Add CORS for frontend
- [ ] Deploy to production

## 🐛 Troubleshooting

### Database Connection Error

```bash
# Check PostgreSQL is running
sudo service postgresql status

# Check database exists
psql -U postgres -l | grep fastapi_db

# Verify credentials in .env match your PostgreSQL setup
```

### Port Already in Use

```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9

# Or use a different port
venv/bin/uvicorn app.main:app --reload --port 8080
```

### Import Errors

```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

## 📄 License

This project is for educational purposes.
