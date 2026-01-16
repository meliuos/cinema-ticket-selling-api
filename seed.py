"""
Database seeding script.

Run this to populate the database with sample data for development/testing.
"""
from datetime import datetime, timedelta, date
from sqlmodel import Session, create_engine, select, text

from app.config import settings
from app.database import engine
from app.models import Cinema, Room, Seat, Movie, Screening, User
from app.services.auth import get_password_hash
from sqlmodel import SQLModel



def seed_database():
    """Seed the database with sample data."""
    print("🌱 Starting database seeding...")
    
    with Session(engine) as session:
        # Check if already seeded
        existing_cinema = session.exec(select(Cinema)).first()
        if existing_cinema:
           print("⚠️  Database already contains data. Skipping seed.")
           return
        
        # Create sample user (for testing ticket booking)
        print("👤 Creating sample user...")
        demo_user = User(
            email="demo@cinema.com",
            full_name="Demo User",
            hashed_password=get_password_hash("demo123"),
            is_active=True
        )
        session.add(demo_user)
        
        # Create admin user
        print("👑 Creating admin user...")
        admin_user = User(
            email="admin@cinema.com",
            full_name="Admin User",
            hashed_password=get_password_hash("admin123"),
            is_active=True,
            is_admin=True
        )
        session.add(admin_user)
        session.commit()
        session.refresh(demo_user)
        session.refresh(admin_user)
        print(f"   ✓ Created user: {demo_user.email}")
        print(f"   ✓ Created user: {demo_user.email}")
        print(f"   ✓ Created admin: {admin_user.email}")

        # Create cinemas
        print("\n🎬 Creating cinemas...")
        cinemas = [
            Cinema(
                name="Mega Cinema Tunis",
                address="123 Avenue Habib Bourguiba",
                city="Tunis",
                phone="+216 71 123 456",
                hasParking=True,
                isAccessible=True,
                amenities=["IMAX", "3D", "Dolby Atmos", "VIP Seats", "Food Court", "Online Booking"]
            ),
            Cinema(
                name="Pathe Palace",
                address="456 Avenue de la Liberte",
                city="Tunis",
                phone="+216 71 234 567",
                hasParking=True,
                isAccessible=True,
                amenities=["IMAX", "4DX", "3D", "Dolby Atmos", "Premium Seats", "Cafe", "Parking"]
            ),
            Cinema(
                name="ABC Cinema Carthage",
                address="Avenue de Carthage, Les Berges du Lac",
                city="Tunis",
                phone="+216 71 345 678",
                hasParking=True,
                isAccessible=True,
                amenities=["3D", "Dolby Surround", "Comfortable Seats", "Snack Bar", "Air Conditioning"]
            ),
            Cinema(
                name="Prestige Cinema Sousse",
                address="Boulevard 14 Janvier, City Center",
                city="Sousse",
                phone="+216 73 456 789",
                hasParking=False,
                isAccessible=True,
                amenities=["3D", "Digital Projection", "Recliner Seats", "Cafe", "Online Tickets"]
            ),
            Cinema(
                name="Madina Cinema Sfax",
                address="Avenue de la Republique",
                city="Sfax",
                phone="+216 74 567 890",
                hasParking=True,
                isAccessible=False,
                amenities=["3D", "Standard Seats", "Concession Stand", "Multiple Screens"]
            ),
            Cinema(
                name="Star Cinema La Marsa",
                address="Route de la Marsa, La Marsa Corniche",
                city="La Marsa",
                phone="+216 71 678 901",
                hasParking=True,
                isAccessible=True,
                amenities=["IMAX", "3D", "Laser Projection", "VIP Lounge", "Restaurant", "Premium Sound"]
            )
        ]
        
        for cinema in cinemas:
            session.add(cinema)
        session.commit()
        
        for cinema in cinemas:
            session.refresh(cinema)
            print(f"   ✓ Created cinema: {cinema.name}")
        
        # Create rooms for first cinema
        print("\n🚪 Creating rooms...")
        rooms = [
            Room(name="Room 1", cinema_id=cinemas[0].id),
            Room(name="Room 2", cinema_id=cinemas[0].id),
            Room(name="IMAX Theater", cinema_id=cinemas[1].id),
            Room(name="4DX Hall", cinema_id=cinemas[1].id),
            Room(name="VIP Room", cinema_id=cinemas[5].id),
        ]
        
        for room in rooms:
            session.add(room)
        session.commit()
        
        for room in rooms:
            session.refresh(room)
            print(f"   ✓ Created room: {room.name} in {[c for c in cinemas if c.id == room.cinema_id][0].name}")
        
        # Create seats for each room
        print("\n💺 Creating seats...")
        total_seats = 0
        for room in rooms:
            # IMAX and VIP rooms: 12 rows x 20 seats, others: 8 rows x 12 seats
            if "IMAX" in room.name or "VIP" in room.name:
                rows = 12
                seats_per_row = 20
            elif "4DX" in room.name:
                rows = 10
                seats_per_row = 16
            else:
                rows = 8
                seats_per_row = 12
            
            for row_num in range(rows):
                row_label = chr(65 + row_num) if row_num < 26 else f"A{chr(65 + row_num - 26)}"
                
                for seat_num in range(1, seats_per_row + 1):
                    # VIP rooms: all VIP seats, others: last 2 rows are VIP
                    if "VIP" in room.name:
                        seat_type = "vip"
                    else:
                        seat_type = "vip" if row_num >= rows - 2 else "standard"
                    seat = Seat(
                        room_id=room.id,
                        row_label=row_label,
                        seat_number=seat_num,
                        seat_type=seat_type
                    )
                    session.add(seat)
                    total_seats += 1
            
            print(f"   ✓ Created {rows * seats_per_row} seats for {room.name}")
        
        session.commit()
        print(f"   Total seats created: {total_seats}")

        # Updated movies with newer release dates
        print("\n🎥 Creating movies with newer release dates...")
        movies = [
            Movie(
                title="Avatar: The Way of Water",
                description="Jake Sully lives with his newfound family formed on Pandora...",
                duration_minutes=192,
                genre="Sci-Fi",
                rating="PG-13",
                cast=["Sam Worthington", "Zoe Saldaña", "Sigourney Weaver"],
                director="James Cameron",
                writers=["James Cameron"],
                producers=["Jon Landau"],
                release_date=date(2022, 12, 16),  # newer date
                country="USA",
                language="English",
                budget=250000000,
                revenue=2300000000,
                production_company="20th Century Studios",
                distributor="20th Century Studios",
                image_url="https://image.tmdb.org/t/p/w500/t6HIqrRAclMCA60NsSmeqe9RmNV.jpg",
                trailer_url="https://www.youtube.com/watch?v=d9MyW72ELq0",
                awards=[],
                details={"imdb_rating": 7.8}
            ),
            Movie(
                title="Oppenheimer",
                description="The story of J. Robert Oppenheimer and the creation of the atomic bomb...",
                duration_minutes=180,
                genre="Biography",
                rating="PG-13",
                cast=["Cillian Murphy", "Emily Blunt", "Matt Damon"],
                director="Christopher Nolan",
                writers=["Christopher Nolan"],
                producers=["Emma Thomas", "Christopher Nolan"],
                release_date=date(2023, 7, 21),  # newer date
                country="USA",
                language="English",
                budget=100000000,
                revenue=900000000,
                production_company="Universal Pictures",
                distributor="Universal Pictures",
                image_url="https://image.tmdb.org/t/p/w500/FiQkXn0i6HsqZfXb4Kt8fhFIdHg.jpg",
                trailer_url="https://www.youtube.com/watch?v=QPdIXok6GOs",
                awards=[],
                details={"imdb_rating": 8.5}
            ),
        ]

        # Create movies with comprehensive details
        print("\n🎥 Creating movies...")
        movies = [
            Movie(
                title="The Matrix",
                description="A computer hacker learns about the true nature of reality and his role in the war against its controllers.",
                duration_minutes=136,
                genre="Sci-Fi",
                rating="R",
                cast=["Keanu Reeves", "Laurence Fishburne", "Carrie-Anne Moss", "Hugo Weaving"],
                director="The Wachowskis",
                writers=["The Wachowskis"],
                producers=["Joel Silver"],
                release_date=date(1999, 3, 31),
                country="USA",
                language="English",
                budget=63000000,
                revenue=466364845,
                production_company="Warner Bros. Pictures",
                distributor="Warner Bros. Pictures",
                image_url="https://image.tmdb.org/t/p/w500/f89U3ADr1oiB1s9GkdPOEpXUk5H.jpg",
                trailer_url="https://www.youtube.com/watch?v=vKQi3bBA1y8",
                awards=["Academy Award for Best Visual Effects", "Academy Award for Best Film Editing"],
                details={"trilogy": "The Matrix Trilogy", "part": 1}
            ),
            Movie(
                title="Inception",
                description="A thief who steals corporate secrets through dream-sharing technology is given the inverse task of planting an idea.",
                duration_minutes=148,
                genre="Sci-Fi",
                rating="PG-13",
                cast=["Leonardo DiCaprio", "Joseph Gordon-Levitt", "Ellen Page", "Tom Hardy", "Marion Cotillard"],
                director="Christopher Nolan",
                writers=["Christopher Nolan"],
                producers=["Emma Thomas", "Christopher Nolan"],
                release_date=date(2010, 7, 16),
                country="USA",
                language="English",
                budget=160000000,
                revenue=836848102,
                production_company="Warner Bros. Pictures",
                distributor="Warner Bros. Pictures",
                image_url="https://image.tmdb.org/t/p/w500/9gk7adHYeDvHkCSEqAvQNLV5Uge.jpg",
                trailer_url="https://www.youtube.com/watch?v=YoHD9XEInc0",
                awards=["Academy Award for Best Cinematography", "Academy Award for Best Sound Mixing"],
                details={"imdb_rating": 8.8, "metascore": 74}
            ),
            Movie(
                title="The Dark Knight",
                description="When the menace known as the Joker wreaks havoc on Gotham, Batman must accept one of the greatest tests.",
                duration_minutes=152,
                genre="Action",
                rating="PG-13",
                cast=["Christian Bale", "Heath Ledger", "Aaron Eckhart", "Michael Caine", "Gary Oldman"],
                director="Christopher Nolan",
                writers=["Jonathan Nolan", "Christopher Nolan"],
                producers=["Emma Thomas", "Charles Roven"],
                release_date=date(2008, 7, 18),
                country="USA",
                language="English",
                budget=185000000,
                revenue=1004558444,
                production_company="Warner Bros. Pictures",
                distributor="Warner Bros. Pictures",
                image_url="https://image.tmdb.org/t/p/w500/qJ2tW6WMUDux911r6m7haRef0WH.jpg",
                trailer_url="https://www.youtube.com/watch?v=EXeTwQWrcwY",
                awards=["Academy Award for Best Supporting Actor (Heath Ledger)", "Academy Award for Best Sound Editing"],
                details={"trilogy": "The Dark Knight Trilogy", "part": 2, "imdb_rating": 9.0}
            ),
            Movie(
                title="Interstellar",
                description="A team of explorers travel through a wormhole in space in an attempt to ensure humanity's survival.",
                duration_minutes=169,
                genre="Sci-Fi",
                rating="PG-13",
                cast=["Matthew McConaughey", "Anne Hathaway", "Jessica Chastain", "Michael Caine", "Matt Damon"],
                director="Christopher Nolan",
                writers=["Jonathan Nolan", "Christopher Nolan"],
                producers=["Emma Thomas", "Christopher Nolan", "Lynda Obst"],
                release_date=date(2014, 11, 7),
                country="USA",
                language="English",
                budget=165000000,
                revenue=677471339,
                production_company="Paramount Pictures",
                distributor="Paramount Pictures",
                image_url="https://image.tmdb.org/t/p/w500/gEU2QniE6E77NI6lCU6MxlNBvIx.jpg",
                trailer_url="https://www.youtube.com/watch?v=zSWdZVtXT7E",
                awards=["Academy Award for Best Visual Effects"],
                details={"imdb_rating": 8.6, "score_composer": "Hans Zimmer"}
            ),
            Movie(
                title="Pulp Fiction",
                description="The lives of two mob hitmen, a boxer, a gangster and his wife intertwine in four tales of violence.",
                duration_minutes=154,
                genre="Crime",
                rating="R",
                cast=["John Travolta", "Samuel L. Jackson", "Uma Thurman", "Bruce Willis", "Ving Rhames"],
                director="Quentin Tarantino",
                writers=["Quentin Tarantino", "Roger Avary"],
                producers=["Lawrence Bender"],
                release_date=date(1994, 10, 14),
                country="USA",
                language="English",
                budget=8000000,
                revenue=213928762,
                production_company="Miramax Films",
                distributor="Miramax Films",
                image_url="https://image.tmdb.org/t/p/w500/d5iIlFn5s0ImszYzBPb8JPIfbXD.jpg",
                trailer_url="https://www.youtube.com/watch?v=s7EdQ4FqbhY",
                awards=["Academy Award for Best Original Screenplay", "Palme d'Or at Cannes"],
                details={"imdb_rating": 8.9, "non_linear_narrative": True}
            )
        ]
        
        for movie in movies:
            session.add(movie)
        session.commit()
        
        for movie in movies:
            session.refresh(movie)
            print(f"   ✓ Created movie: {movie.title}")
        
        # Create screenings (tomorrow and day after tomorrow for all cinemas)
        print("\n📅 Creating screenings...")
        base_date = datetime.now() + timedelta(days=1)
        screening_count = 0
        
        for day in range(2):  # Tomorrow and day after tomorrow
            current_date = base_date + timedelta(days=day)
            
            # Morning, afternoon, evening, night showtimes
            times = [10, 14, 18, 21]
            
            # Create screenings for all rooms (covering all cinemas)
            for room_idx, room in enumerate(rooms):
                # Distribute movies across rooms
                movie = movies[room_idx % len(movies)]
                
                for time_hour in times:
                    screening_time = current_date.replace(hour=time_hour, minute=0, second=0)
                    
                    # Premium rooms cost more
                    if "IMAX" in room.name:
                        base_price = 22.0
                    elif "VIP" in room.name:
                        base_price = 25.0
                    elif "4DX" in room.name:
                        base_price = 20.0
                    else:
                        base_price = 15.0
                    
                    # Evening/night shows cost more
                    price = base_price + 3.0 if time_hour >= 18 else base_price
                    
                    screening = Screening(
                        movie_id=movie.id,
                        room_id=room.id,
                        screening_time=screening_time,
                        price=price
                    )
                    session.add(screening)
                    screening_count += 1
        
        session.commit()
        print(f"   ✓ Created {screening_count} screenings across all cinemas")
        
        print("\n✅ Database seeding completed successfully!")
        print(f"\n📊 Summary:")
        print(f"   - {len(cinemas)} cinemas")
        print(f"   - {len(rooms)} rooms")
        print(f"   - {total_seats} seats")
        print(f"   - {len(movies)} movies (with enhanced details)")
        print(f"   - {screening_count} screenings")
        print(f"   - 1 demo user (email: demo@cinema.com, password: demo123)")


if __name__ == "__main__":
    with Session(engine) as session:
        print("🧹 Deleting previous data...")

        # Delete screenings first (due to foreign key constraints)
        session.exec(text('DELETE FROM screening'))
        session.exec(text('DELETE FROM seat'))
        session.exec(text('DELETE FROM room'))
        session.exec(text('DELETE FROM movie'))
        session.exec(text('DELETE FROM cinema'))
        session.exec(text('DELETE FROM "user"'))
        session.commit()

        print("   ✓ All previous data deleted")

    seed_database()
