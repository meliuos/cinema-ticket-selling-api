"""
Database seeding script.

Run this to populate the database with sample data for development/testing.
"""
from datetime import datetime, timedelta, date
from sqlmodel import Session, create_engine, select

from app.config import settings
from app.database import engine
from app.models import Cinema, Room, Seat, Movie, Screening, User, Cast, Ticket, Review, Favorite, SearchHistory, TokenBlacklist
from app.models.movie import MovieState
from app.models.review import ReviewReactionModel
from app.services.auth import get_password_hash


def clear_database(session: Session):
    """Clear all data from the database to avoid duplicates."""
    print("🗑️  Clearing existing data...")
    
    # Delete in order of dependencies (most dependent first)
    from sqlalchemy import text
    
    # Disable foreign key checks temporarily for PostgreSQL
    session.execute(text("SET session_replication_role = 'replica';"))
    
    # Delete all data
    session.execute(text("DELETE FROM tokenblacklist;"))
    session.execute(text("DELETE FROM search_history;"))
    session.execute(text("DELETE FROM favorite;"))
    session.execute(text("DELETE FROM review_reactions;"))
    session.execute(text("DELETE FROM reviews;"))
    session.execute(text("DELETE FROM ticket;"))
    session.execute(text('DELETE FROM "cast";'))
    session.execute(text("DELETE FROM screening;"))
    session.execute(text("DELETE FROM seat;"))
    session.execute(text("DELETE FROM room;"))
    session.execute(text("DELETE FROM cinema;"))
    session.execute(text("DELETE FROM movie;"))
    session.execute(text('DELETE FROM "user";'))
    
    # Re-enable foreign key checks
    session.execute(text("SET session_replication_role = 'origin';"))
    
    session.commit()
    print("   ✓ All existing data cleared")


def seed_database():
    """Seed the database with sample data."""
    print("🌱 Starting database seeding...")
    
    with Session(engine) as session:
        # Clear existing data to avoid duplicates
        clear_database(session)
        
        # Create sample user (for testing ticket booking)
        print("\n👤 Creating sample user...")
        demo_user = User(
            email="demo@cinema.com",
            full_name="Demo User",
            hashed_password=get_password_hash("demo123"),
            is_active=True
        )
        session.add(demo_user)
        session.commit()
        session.refresh(demo_user)
        print(f"   ✓ Created user: {demo_user.email}")
        
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
        session.refresh(admin_user)
        print(f"   ✓ Created admin: {admin_user.email}")
        
        # Create cinemas
        print("\n🎬 Creating cinemas...")
        cinema_data = [
            {
                "name": "Mega Cinema Tunis",
                "address": "123 Avenue Habib Bourguiba",
                "city": "Tunis",
                "phone": "+216 71 123 456",
                "hasParking": True,
                "isAccessible": True,
                "amenities": ["WiFi", "Café", "Parking", "3D", "IMAX"]
            },
            {
                "name": "Pathé Palace Tunis",
                "address": "456 Avenue de la Liberté",
                "city": "Tunis",
                "phone": "+216 71 234 567",
                "hasParking": False,
                "isAccessible": True,
                "amenities": ["WiFi", "Bar", "VIP Lounge", "Dolby Atmos"]
            },
            {
                "name": "Cinema Africa",
                "address": "789 Rue de Carthage",
                "city": "Tunis",
                "phone": "+216 71 345 678",
                "hasParking": True,
                "isAccessible": False,
                "amenities": ["WiFi", "Restaurant", "Parking"]
            },
            {
                "name": "Star Cinema Sfax",
                "address": "321 Boulevard 14 Janvier",
                "city": "Sfax",
                "phone": "+216 74 456 789",
                "hasParking": True,
                "isAccessible": True,
                "amenities": ["WiFi", "Parking", "Café", "3D"]
            },
            {
                "name": "Royal Cinema Sousse",
                "address": "654 Avenue Habib Bourguiba",
                "city": "Sousse",
                "phone": "+216 73 567 890",
                "hasParking": False,
                "isAccessible": True,
                "amenities": ["WiFi", "Bar", "VIP Lounge"]
            },
            {
                "name": "Cinémax Nabeul",
                "address": "101 Avenue Farhat Hached",
                "city": "Nabeul",
                "phone": "+216 72 678 901",
                "hasParking": True,
                "isAccessible": True,
                "amenities": ["WiFi", "Café", "Parking"]
            },
            {
                "name": "Grand Cinema Bizerte",
                "address": "202 Rue de la République",
                "city": "Bizerte",
                "phone": "+216 72 789 012",
                "hasParking": True,
                "isAccessible": True,
                "amenities": ["WiFi", "Restaurant", "Parking", "3D"]
            },
            {
                "name": "Imperial Cinema Monastir",
                "address": "303 Avenue Habib Bourguiba",
                "city": "Monastir",
                "phone": "+216 73 890 123",
                "hasParking": False,
                "isAccessible": True,
                "amenities": ["WiFi", "Café", "VIP Lounge"]
            },
            {
                "name": "Cinema Le Palace Tunis",
                "address": "45 Avenue Mohamed V",
                "city": "Tunis",
                "phone": "+216 71 456 123",
                "hasParking": True,
                "isAccessible": True,
                "amenities": ["WiFi", "Café", "Parking", "4DX"]
            },
            {
                "name": "Cinéma Les Ambassadeurs",
                "address": "78 Rue de Marseille",
                "city": "Tunis",
                "phone": "+216 71 567 234",
                "hasParking": False,
                "isAccessible": True,
                "amenities": ["WiFi", "Bar", "VIP Lounge"]
            },
            {
                "name": "Cineplex La Marsa",
                "address": "12 Avenue de la Corniche",
                "city": "La Marsa",
                "phone": "+216 71 678 345",
                "hasParking": True,
                "isAccessible": True,
                "amenities": ["WiFi", "Restaurant", "Parking", "3D", "IMAX"]
            },
            {
                "name": "Cinema Cosmos Ariana",
                "address": "89 Avenue de la République",
                "city": "Ariana",
                "phone": "+216 71 789 456",
                "hasParking": True,
                "isAccessible": True,
                "amenities": ["WiFi", "Café", "Parking", "Dolby Atmos"]
            },
            {
                "name": "Star Cinéma Ben Arous",
                "address": "23 Boulevard de l'Environnement",
                "city": "Ben Arous",
                "phone": "+216 79 890 567",
                "hasParking": True,
                "isAccessible": True,
                "amenities": ["WiFi", "Parking", "Café"]
            },
            {
                "name": "Cinéma Colisée Sfax",
                "address": "56 Avenue Majida Boulila",
                "city": "Sfax",
                "phone": "+216 74 901 678",
                "hasParking": False,
                "isAccessible": True,
                "amenities": ["WiFi", "Bar", "3D"]
            },
            {
                "name": "Cinéma Le Rio Gabès",
                "address": "34 Avenue Farhat Hached",
                "city": "Gabès",
                "phone": "+216 75 012 789",
                "hasParking": True,
                "isAccessible": True,
                "amenities": ["WiFi", "Café", "Parking"]
            },
            {
                "name": "Cinema Plaza Hammamet",
                "address": "67 Avenue de la Paix",
                "city": "Hammamet",
                "phone": "+216 72 123 890",
                "hasParking": True,
                "isAccessible": True,
                "amenities": ["WiFi", "Restaurant", "Parking", "3D"]
            },
            {
                "name": "Cinéma ABC Kairouan",
                "address": "90 Avenue de la République",
                "city": "Kairouan",
                "phone": "+216 77 234 901",
                "hasParking": True,
                "isAccessible": False,
                "amenities": ["WiFi", "Café"]
            },
            {
                "name": "Pathé Manar Tunis",
                "address": "11 Centre Commercial Manar City",
                "city": "Tunis",
                "phone": "+216 71 345 012",
                "hasParking": True,
                "isAccessible": True,
                "amenities": ["WiFi", "Food Court", "Parking", "IMAX", "4DX"]
            },
            {
                "name": "Cinema Odyssée Sousse",
                "address": "22 Boulevard de la Corniche",
                "city": "Sousse",
                "phone": "+216 73 456 123",
                "hasParking": True,
                "isAccessible": True,
                "amenities": ["WiFi", "Restaurant", "Parking", "VIP Lounge"]
            },
            {
                "name": "Cinéma El Hamra Tozeur",
                "address": "44 Avenue Abou El Kacem Chebbi",
                "city": "Tozeur",
                "phone": "+216 76 567 234",
                "hasParking": True,
                "isAccessible": True,
                "amenities": ["WiFi", "Café", "Parking"]
            },
            {
                "name": "CinéCity Manouba",
                "address": "55 Avenue de l'Indépendance",
                "city": "Manouba",
                "phone": "+216 71 678 345",
                "hasParking": True,
                "isAccessible": True,
                "amenities": ["WiFi", "Parking", "Café", "3D"]
            },
            {
                "name": "Cinema Liberty Mahdia",
                "address": "66 Avenue Habib Bourguiba",
                "city": "Mahdia",
                "phone": "+216 73 789 456",
                "hasParking": False,
                "isAccessible": True,
                "amenities": ["WiFi", "Bar"]
            },
            {
                "name": "Cineplex Carthage",
                "address": "77 Avenue des Thermes d'Antonin",
                "city": "Carthage",
                "phone": "+216 71 890 567",
                "hasParking": True,
                "isAccessible": True,
                "amenities": ["WiFi", "Restaurant", "Parking", "IMAX", "VIP Lounge"]
            },
            {
                "name": "Star Cinema Kef",
                "address": "88 Avenue Habib Bourguiba",
                "city": "Kef",
                "phone": "+216 78 901 678",
                "hasParking": True,
                "isAccessible": True,
                "amenities": ["WiFi", "Café", "Parking"]
            },
            {
                "name": "Cinéma Atlas Gafsa",
                "address": "99 Boulevard de l'Environnement",
                "city": "Gafsa",
                "phone": "+216 76 012 789",
                "hasParking": True,
                "isAccessible": False,
                "amenities": ["WiFi", "Parking"]
            },
            {
                "name": "Cinema Horizon Médenine",
                "address": "10 Avenue 7 Novembre",
                "city": "Médenine",
                "phone": "+216 75 123 890",
                "hasParking": True,
                "isAccessible": True,
                "amenities": ["WiFi", "Café", "Parking", "3D"]
            },
            {
                "name": "Cinéma Le Capitol Zaghouan",
                "address": "21 Avenue de la Liberté",
                "city": "Zaghouan",
                "phone": "+216 72 234 901",
                "hasParking": False,
                "isAccessible": True,
                "amenities": ["WiFi", "Café"]
            },
            {
                "name": "Cinema Moderne Jendouba",
                "address": "32 Rue de la République",
                "city": "Jendouba",
                "phone": "+216 78 345 012",
                "hasParking": True,
                "isAccessible": True,
                "amenities": ["WiFi", "Parking", "Café"]
            },
            {
                "name": "Cinéma Royal Kasserine",
                "address": "43 Avenue Habib Bourguiba",
                "city": "Kasserine",
                "phone": "+216 77 456 123",
                "hasParking": True,
                "isAccessible": True,
                "amenities": ["WiFi", "Café", "Parking", "3D"]
            },
            {
                "name": "Star Cinéma Tataouine",
                "address": "54 Avenue de l'Indépendance",
                "city": "Tataouine",
                "phone": "+216 75 567 234",
                "hasParking": True,
                "isAccessible": False,
                "amenities": ["WiFi", "Parking"]
            }
        ]
        
        cinemas = []
        for data in cinema_data:
            cinema = Cinema(**data)
            session.add(cinema)
            session.commit()
            session.refresh(cinema)
            cinemas.append(cinema)
            print(f"   ✓ Created cinema: {cinema.name}")
        
        # Create rooms for each cinema
        print("\n🚪 Creating rooms...")
        rooms = []
        room_names = ["Room 1", "Room 2", "Room 3", "IMAX", "VIP", "3D Room"]
        
        for cinema in cinemas:
            # Bigger cities get more rooms
            if cinema.city == "Tunis":
                num_rooms = 4
            elif cinema.city in ["Sfax", "Sousse"]:
                num_rooms = 3
            else:
                num_rooms = 2
            
            for i in range(num_rooms):
                room_name = room_names[i % len(room_names)]
                room = Room(name=room_name, cinema_id=cinema.id)
                session.add(room)
                rooms.append(room)
            
            session.commit()
            print(f"   ✓ Added {num_rooms} rooms to {cinema.name}")
        
        # Refresh all rooms
        for room in rooms:
            session.refresh(room)
        
        # Create seats for each room - 7 rows x 10 seats
        print("\n💺 Creating seats (7 rows x 10 seats each)...")
        total_seats = 0
        
        for room in rooms:
            # Always create 7 rows x 10 seats for all rooms
            rows = 7
            seats_per_row = 10
            
            for row_num in range(rows):
                row_label = chr(65 + row_num) if row_num < 26 else f"A{chr(65 + row_num - 26)}"
                
                for seat_num in range(1, seats_per_row + 1):
                    seat = Seat(
                        room_id=room.id,
                        row_label=row_label,
                        seat_number=seat_num,
                        seat_type="standard"
                    )
                    session.add(seat)
                    total_seats += 1
        
        session.commit()
        print(f"   ✓ Created {total_seats} seats ({rows} rows x {seats_per_row} seats per room)")
        
        # Create movies with comprehensive details
        print("\n🎥 Creating movies...")
        movies_data = [
            {
                "title": "The Matrix",
                "description": "A computer hacker learns about the true nature of reality and his role in the war against its controllers.",
                "duration_minutes": 136,
                "genre": ["Sci-Fi", "Action"],
                "rating": "R",
                "cast": ["Keanu Reeves", "Laurence Fishburne", "Carrie-Anne Moss", "Hugo Weaving"],
                "director": "The Wachowskis",
                "writers": ["The Wachowskis"],
                "producers": ["Joel Silver"],
                "release_date": date(1999, 3, 31),
                "country": "USA",
                "language": "English",
                "budget": 63000000,
                "revenue": 466364845,
                "production_company": "Warner Bros. Pictures",
                "distributor": "Warner Bros. Pictures",
                "image_url": "https://image.tmdb.org/t/p/w500/f89U3ADr1oiB1s9GkdPOEpXUk5H.jpg",
                "trailer_url": "https://www.youtube.com/watch?v=vKQi3bBA1y8",
                "awards": ["Academy Award for Best Visual Effects", "Academy Award for Best Film Editing"],
                "details": {"trilogy": "The Matrix Trilogy", "part": 1}
            },
            {
                "title": "Inception",
                "description": "A thief who steals corporate secrets through dream-sharing technology is given the inverse task of planting an idea.",
                "duration_minutes": 148,
                "genre": ["Sci-Fi", "Thriller"],
                "rating": "PG-13",
                "cast": ["Leonardo DiCaprio", "Joseph Gordon-Levitt", "Ellen Page", "Tom Hardy", "Marion Cotillard"],
                "director": "Christopher Nolan",
                "writers": ["Christopher Nolan"],
                "producers": ["Emma Thomas", "Christopher Nolan"],
                "release_date": date(2010, 7, 16),
                "country": "USA",
                "language": "English",
                "budget": 160000000,
                "revenue": 836848102,
                "production_company": "Warner Bros. Pictures",
                "distributor": "Warner Bros. Pictures",
                "image_url": "https://image.tmdb.org/t/p/w500/9gk7adHYeDvHkCSEqAvQNLV5Uge.jpg",
                "trailer_url": "https://www.youtube.com/watch?v=YoHD9XEInc0",
                "awards": ["Academy Award for Best Cinematography", "Academy Award for Best Sound Mixing"],
                "details": {"imdb_rating": 8.8, "metascore": 74}
            },
            {
                "title": "The Dark Knight",
                "description": "When the menace known as the Joker wreaks havoc on Gotham, Batman must accept one of the greatest tests.",
                "duration_minutes": 152,
                "genre": ["Action", "Crime", "Drama"],
                "rating": "PG-13",
                "cast": ["Christian Bale", "Heath Ledger", "Aaron Eckhart", "Michael Caine", "Gary Oldman"],
                "director": "Christopher Nolan",
                "writers": ["Jonathan Nolan", "Christopher Nolan"],
                "producers": ["Emma Thomas", "Charles Roven"],
                "release_date": date(2008, 7, 18),
                "country": "USA",
                "language": "English",
                "budget": 185000000,
                "revenue": 1004558444,
                "production_company": "Warner Bros. Pictures",
                "distributor": "Warner Bros. Pictures",
                "image_url": "https://image.tmdb.org/t/p/w500/qJ2tW6WMUDux911r6m7haRef0WH.jpg",
                "trailer_url": "https://www.youtube.com/watch?v=EXeTwQWrcwY",
                "awards": ["Academy Award for Best Supporting Actor (Heath Ledger)", "Academy Award for Best Sound Editing"],
                "details": {"trilogy": "The Dark Knight Trilogy", "part": 2, "imdb_rating": 9.0}
            },
            {
                "title": "Interstellar",
                "description": "A team of explorers travel through a wormhole in space in an attempt to ensure humanity's survival.",
                "duration_minutes": 169,
                "genre": ["Sci-Fi", "Drama"],
                "rating": "PG-13",
                "cast": ["Matthew McConaughey", "Anne Hathaway", "Jessica Chastain", "Michael Caine", "Matt Damon"],
                "director": "Christopher Nolan",
                "writers": ["Jonathan Nolan", "Christopher Nolan"],
                "producers": ["Emma Thomas", "Christopher Nolan", "Lynda Obst"],
                "release_date": date(2014, 11, 7),
                "country": "USA",
                "language": "English",
                "budget": 165000000,
                "revenue": 677471339,
                "production_company": "Paramount Pictures",
                "distributor": "Paramount Pictures",
                "image_url": "https://image.tmdb.org/t/p/w500/gEU2QniE6E77NI6lCU6MxlNBvIx.jpg",
                "trailer_url": "https://www.youtube.com/watch?v=zSWdZVtXT7E",
                "awards": ["Academy Award for Best Visual Effects"],
                "details": {"imdb_rating": 8.6, "score_composer": "Hans Zimmer"}
            },
            {
                "title": "Pulp Fiction",
                "description": "The lives of two mob hitmen, a boxer, a gangster and his wife intertwine in four tales of violence.",
                "duration_minutes": 154,
                "genre": ["Crime", "Drama"],
                "rating": "R",
                "cast": ["John Travolta", "Samuel L. Jackson", "Uma Thurman", "Bruce Willis", "Ving Rhames"],
                "director": "Quentin Tarantino",
                "writers": ["Quentin Tarantino", "Roger Avary"],
                "producers": ["Lawrence Bender"],
                "release_date": date(1994, 10, 14),
                "country": "USA",
                "language": "English",
                "budget": 8000000,
                "revenue": 213928762,
                "production_company": "Miramax Films",
                "distributor": "Miramax Films",
                "image_url": "https://image.tmdb.org/t/p/w500/d5iIlFn5s0ImszYzBPb8JPIfbXD.jpg",
                "trailer_url": "https://www.youtube.com/watch?v=s7EdQ4FqbhY",
                "awards": ["Academy Award for Best Original Screenplay", "Palme d'Or at Cannes"],
                "details": {"imdb_rating": 8.9, "non_linear_narrative": True}
            },
            {
                "title": "The Shawshank Redemption",
                "description": "Two imprisoned men bond over a number of years, finding solace and eventual redemption through acts of common decency.",
                "duration_minutes": 142,
                "genre": ["Drama"],
                "rating": "R",
                "cast": ["Tim Robbins", "Morgan Freeman", "Bob Gunton", "William Sadler"],
                "director": "Frank Darabont",
                "writers": ["Frank Darabont"],
                "producers": ["Niki Marvin"],
                "release_date": date(1994, 9, 23),
                "country": "USA",
                "language": "English",
                "budget": 25000000,
                "revenue": 28341469,
                "production_company": "Castle Rock Entertainment",
                "distributor": "Columbia Pictures",
                "image_url": "https://image.tmdb.org/t/p/w500/q6y0Go1tsGEsmtFryDOJo3dEmqu.jpg",
                "trailer_url": "https://www.youtube.com/watch?v=6hB3S9bIaco",
                "awards": ["Nominated for 7 Academy Awards"],
                "details": {"imdb_rating": 9.3}
            },
            {
                "title": "Forrest Gump",
                "description": "The presidencies of Kennedy and Johnson, Vietnam, Watergate, and other history unfold through the perspective of an Alabama man.",
                "duration_minutes": 142,
                "genre": ["Drama", "Romance"],
                "rating": "PG-13",
                "cast": ["Tom Hanks", "Robin Wright", "Gary Sinise", "Sally Field"],
                "director": "Robert Zemeckis",
                "writers": ["Winston Groom", "Eric Roth"],
                "producers": ["Wendy Finerman", "Steve Tisch"],
                "release_date": date(1994, 7, 6),
                "country": "USA",
                "language": "English",
                "budget": 55000000,
                "revenue": 677387716,
                "production_company": "Paramount Pictures",
                "distributor": "Paramount Pictures",
                "image_url": "https://image.tmdb.org/t/p/w500/arw2vcBveWOVZr6pxd9XTd1TdQa.jpg",
                "trailer_url": "https://www.youtube.com/watch?v=bLvqoHBptjg",
                "awards": ["Academy Award for Best Picture", "Academy Award for Best Director"],
                "details": {"imdb_rating": 8.8}
            },
            {
                "title": "The Godfather",
                "description": "The aging patriarch of an organized crime dynasty transfers control of his clandestine empire to his reluctant son.",
                "duration_minutes": 175,
                "genre": ["Crime", "Drama"],
                "rating": "R",
                "cast": ["Marlon Brando", "Al Pacino", "James Caan", "Richard S. Castellano"],
                "director": "Francis Ford Coppola",
                "writers": ["Mario Puzo", "Francis Ford Coppola"],
                "producers": ["Albert S. Ruddy"],
                "release_date": date(1972, 3, 24),
                "country": "USA",
                "language": "English",
                "budget": 6000000,
                "revenue": 134966411,
                "production_company": "Paramount Pictures",
                "distributor": "Paramount Pictures",
                "image_url": "https://image.tmdb.org/t/p/w500/3bhkrj58Vtu7enYsRolD1fZdja1.jpg",
                "trailer_url": "https://www.youtube.com/watch?v=sY1S34973zI",
                "awards": ["Academy Award for Best Picture", "Academy Award for Best Actor"],
                "details": {"imdb_rating": 9.2, "trilogy": "The Godfather Trilogy", "part": 1}
            },
            {
                "title": "Schindler's List",
                "description": "In German-occupied Poland during World War II, Oskar Schindler gradually becomes concerned for his Jewish workforce.",
                "duration_minutes": 195,
                "genre": ["Biography", "Drama", "History"],
                "rating": "R",
                "cast": ["Liam Neeson", "Ralph Fiennes", "Ben Kingsley", "Caroline Goodall"],
                "director": "Steven Spielberg",
                "writers": ["Steven Zaillian"],
                "producers": ["Steven Spielberg", "Gerald R. Molen"],
                "release_date": date(1993, 12, 15),
                "country": "USA",
                "language": "English",
                "budget": 22000000,
                "revenue": 321365567,
                "production_company": "Universal Pictures",
                "distributor": "Universal Pictures",
                "image_url": "https://image.tmdb.org/t/p/w500/c8Ass7acuSr64EmwAdpinPXapiH.jpg",
                "trailer_url": "https://www.youtube.com/watch?v=JdRGC-w9syA",
                "awards": ["Academy Award for Best Picture", "Academy Award for Best Director"],
                "details": {"imdb_rating": 8.9, "based_on": "Schindler's Ark by Thomas Keneally"}
            },
            {
                "title": "Fight Club",
                "description": "An insomniac office worker and a devil-may-care soapmaker form an underground fight club.",
                "duration_minutes": 139,
                "genre": ["Drama"],
                "rating": "R",
                "cast": ["Brad Pitt", "Edward Norton", "Helena Bonham Carter", "Meat Loaf"],
                "director": "David Fincher",
                "writers": ["Chuck Palahniuk", "Jim Uhls"],
                "producers": ["Art Linson", "Ceán Chaffin"],
                "release_date": date(1999, 10, 15),
                "country": "USA",
                "language": "English",
                "budget": 63000000,
                "revenue": 100853753,
                "production_company": "20th Century Fox",
                "distributor": "20th Century Fox",
                "image_url": "https://image.tmdb.org/t/p/w500/pB8BM7pdSp6B6Ih7QZ4DrQ3PmJK.jpg",
                "trailer_url": "https://www.youtube.com/watch?v=SUXWAEX2jlg",
                "awards": ["Nominated for Academy Award for Best Effects"],
                "details": {"imdb_rating": 8.8, "based_on": "Fight Club by Chuck Palahniuk"}
            },
            {
                "title": "The Lord of the Rings: The Fellowship of the Ring",
                "description": "A meek Hobbit from the Shire and eight companions set out on a journey to destroy the powerful One Ring.",
                "duration_minutes": 178,
                "genre": ["Adventure", "Drama", "Fantasy"],
                "rating": "PG-13",
                "cast": ["Elijah Wood", "Ian McKellen", "Orlando Bloom", "Sean Bean"],
                "director": "Peter Jackson",
                "writers": ["J.R.R. Tolkien", "Fran Walsh", "Philippa Boyens"],
                "producers": ["Peter Jackson", "Fran Walsh"],
                "release_date": date(2001, 12, 19),
                "country": "New Zealand",
                "language": "English",
                "budget": 93000000,
                "revenue": 871368364,
                "production_company": "New Line Cinema",
                "distributor": "New Line Cinema",
                "image_url": "https://image.tmdb.org/t/p/w500/6oom5QYQ2yQTMJIbnvbkBL9cHo6.jpg",
                "trailer_url": "https://www.youtube.com/watch?v=V75dMMIW2B4",
                "awards": ["Academy Award for Best Cinematography", "Academy Award for Best Makeup"],
                "details": {"trilogy": "The Lord of the Rings", "part": 1, "imdb_rating": 8.8}
            },
            {
                "title": "Gladiator",
                "description": "A former Roman General sets out to exact vengeance against the corrupt emperor who murdered his family.",
                "duration_minutes": 155,
                "genre": ["Action", "Adventure", "Drama"],
                "rating": "R",
                "cast": ["Russell Crowe", "Joaquin Phoenix", "Connie Nielsen", "Oliver Reed"],
                "director": "Ridley Scott",
                "writers": ["David Franzoni", "John Logan", "William Nicholson"],
                "producers": ["Douglas Wick", "David Franzoni", "Branko Lustig"],
                "release_date": date(2000, 5, 5),
                "country": "USA",
                "language": "English",
                "budget": 103000000,
                "revenue": 460583960,
                "production_company": "DreamWorks Pictures",
                "distributor": "Universal Pictures",
                "image_url": "https://image.tmdb.org/t/p/w500/ty8TGRuvJLPUmAR1H1nRIsgwvim.jpg",
                "trailer_url": "https://www.youtube.com/watch?v=owK1qxDselE",
                "awards": ["Academy Award for Best Picture", "Academy Award for Best Actor (Russell Crowe)"],
                "details": {"imdb_rating": 8.5}
            },
            {
                "title": "Avatar",
                "description": "A paraplegic Marine dispatched to the moon Pandora on a unique mission becomes torn between following his orders and protecting the world he feels is his home.",
                "duration_minutes": 162,
                "genre": ["Action", "Adventure", "Fantasy", "Sci-Fi"],
                "rating": "PG-13",
                "cast": ["Sam Worthington", "Zoe Saldana", "Sigourney Weaver", "Stephen Lang"],
                "director": "James Cameron",
                "writers": ["James Cameron"],
                "producers": ["James Cameron", "Jon Landau"],
                "release_date": date(2009, 12, 18),
                "country": "USA",
                "language": "English",
                "budget": 237000000,
                "revenue": 2923706026,
                "production_company": "20th Century Fox",
                "distributor": "20th Century Fox",
                "image_url": "https://image.tmdb.org/t/p/w500/kyeqWdyUXW608qlYkRqosgbbJyK.jpg",
                "trailer_url": "https://www.youtube.com/watch?v=5PSNL1qE6VY",
                "awards": ["Academy Award for Best Cinematography", "Academy Award for Best Visual Effects"],
                "details": {"imdb_rating": 7.9, "highest_grossing": True}
            },
            {
                "title": "Titanic",
                "description": "A seventeen-year-old aristocrat falls in love with a kind but poor artist aboard the luxurious, ill-fated R.M.S. Titanic.",
                "duration_minutes": 194,
                "genre": ["Drama", "Romance"],
                "rating": "PG-13",
                "cast": ["Leonardo DiCaprio", "Kate Winslet", "Billy Zane", "Kathy Bates"],
                "director": "James Cameron",
                "writers": ["James Cameron"],
                "producers": ["James Cameron", "Jon Landau"],
                "release_date": date(1997, 12, 19),
                "country": "USA",
                "language": "English",
                "budget": 200000000,
                "revenue": 2264743305,
                "production_company": "20th Century Fox",
                "distributor": "Paramount Pictures",
                "image_url": "https://image.tmdb.org/t/p/w500/9xjZS2rlVxm8SFx8kPC3aIGCOYQ.jpg",
                "trailer_url": "https://www.youtube.com/watch?v=2e-eXJ6HgkQ",
                "awards": ["Academy Award for Best Picture", "Academy Award for Best Director"],
                "details": {"imdb_rating": 7.9, "record_breaking": True}
            },
            {
                "title": "The Green Mile",
                "description": "The lives of guards on Death Row are affected by one of their charges: a black man accused of child murder who has mysterious powers.",
                "duration_minutes": 189,
                "genre": ["Crime", "Drama", "Fantasy"],
                "rating": "R",
                "cast": ["Tom Hanks", "Michael Clarke Duncan", "David Morse", "Bonnie Hunt"],
                "director": "Frank Darabont",
                "writers": ["Stephen King", "Frank Darabont"],
                "producers": ["Frank Darabont", "David Valdes"],
                "release_date": date(1999, 12, 10),
                "country": "USA",
                "language": "English",
                "budget": 60000000,
                "revenue": 286801374,
                "production_company": "Warner Bros. Pictures",
                "distributor": "Warner Bros. Pictures",
                "image_url": "https://image.tmdb.org/t/p/w500/velWPhVMQeQKcxggNEU8YmIo52R.jpg",
                "trailer_url": "https://www.youtube.com/watch?v=Ki4haFrqSrw",
                "awards": ["Nominated for 4 Academy Awards"],
                "details": {"imdb_rating": 8.6}
            },
            {
                "title": "Parasite",
                "description": "Greed and class discrimination threaten the newly formed symbiotic relationship between the wealthy Park family and the destitute Kim clan.",
                "duration_minutes": 132,
                "genre": ["Comedy", "Drama", "Thriller"],
                "rating": "R",
                "cast": ["Song Kang-ho", "Lee Sun-kyun", "Cho Yeo-jeong", "Choi Woo-shik"],
                "director": "Bong Joon-ho",
                "writers": ["Bong Joon-ho", "Han Jin-won"],
                "producers": ["Kwak Sin-ae", "Moon Yang-kwon", "Jang Young-hwan"],
                "release_date": date(2019, 5, 30),
                "country": "South Korea",
                "language": "Korean",
                "budget": 11400000,
                "revenue": 258680152,
                "production_company": "Barunson E&A",
                "distributor": "CJ Entertainment",
                "image_url": "https://image.tmdb.org/t/p/w500/7IiTTgloJzvGI1TAYymCfbfl3vT.jpg",
                "trailer_url": "https://www.youtube.com/watch?v=5xH0HfJHsaY",
                "awards": ["Academy Award for Best Picture", "Academy Award for Best Director", "Palme d'Or at Cannes"],
                "details": {"imdb_rating": 8.5, "first_foreign_language_best_picture": True}
            },
            # Additional Normal Movies (with past release dates)
            {
                "title": "The Lion King",
                "description": "Lion prince Simba and his father are targeted by his bitter uncle, who wants to ascend the throne himself.",
                "duration_minutes": 118,
                "genre": ["Animation", "Adventure", "Drama"],
                "rating": "G",
                "cast": ["Matthew Broderick", "Jeremy Irons", "James Earl Jones", "Whoopi Goldberg"],
                "director": "Roger Allers",
                "writers": ["Irene Mecchi", "Jonathan Roberts", "Linda Woolverton"],
                "producers": ["Don Hahn"],
                "release_date": date(1994, 6, 24),
                "country": "USA",
                "language": "English",
                "budget": 45000000,
                "revenue": 968511805,
                "production_company": "Walt Disney Pictures",
                "distributor": "Buena Vista Pictures",
                "image_url": "https://image.tmdb.org/t/p/w500/sKCr78MXSLixwmZ8DyJLrpMsd15.jpg",
                "trailer_url": "https://www.youtube.com/watch?v=4sj1MT05lAA",
                "awards": ["Academy Award for Best Original Score"],
                "details": {"imdb_rating": 8.5, "animated_classic": True}
            },
            {
                "title": "Jurassic Park",
                "description": "A pragmatic paleontologist visiting an almost complete theme park is tasked with protecting a couple of kids after a power failure causes the park's cloned dinosaurs to run loose.",
                "duration_minutes": 127,
                "genre": ["Action", "Adventure", "Sci-Fi"],
                "rating": "PG-13",
                "cast": ["Sam Neill", "Laura Dern", "Jeff Goldblum", "Richard Attenborough"],
                "director": "Steven Spielberg",
                "writers": ["Michael Crichton", "David Koepp"],
                "producers": ["Kathleen Kennedy", "Gerald R. Molen"],
                "release_date": date(1993, 6, 11),
                "country": "USA",
                "language": "English",
                "budget": 63000000,
                "revenue": 1044866826,
                "production_company": "Universal Pictures",
                "distributor": "Universal Pictures",
                "image_url": "https://image.tmdb.org/t/p/w500/oU7Oq2kFAAlGqbU4VoAE36g4hoI.jpg",
                "trailer_url": "https://www.youtube.com/watch?v=lc0UehYemQA",
                "awards": ["Academy Award for Best Sound", "Academy Award for Best Visual Effects"],
                "details": {"imdb_rating": 8.2, "blockbuster": True}
            },
            {
                "title": "The Silence of the Lambs",
                "description": "A young F.B.I. cadet must receive the help of an incarcerated and manipulative cannibal killer to help catch another serial killer, a madman who skins his victims.",
                "duration_minutes": 118,
                "genre": ["Crime", "Drama", "Thriller"],
                "rating": "R",
                "cast": ["Jodie Foster", "Anthony Hopkins", "Lawrence A. Bonney", "Kasi Lemmons"],
                "director": "Jonathan Demme",
                "writers": ["Thomas Harris", "Ted Tally"],
                "producers": ["Edward Saxon", "Kenneth Utt", "Ron Bozman"],
                "release_date": date(1991, 2, 14),
                "country": "USA",
                "language": "English",
                "budget": 19000000,
                "revenue": 272742922,
                "production_company": "Orion Pictures",
                "distributor": "Orion Pictures",
                "image_url": "https://image.tmdb.org/t/p/w500/uS9m8OBk1A8eM9I042bx8XXpqAq.jpg",
                "trailer_url": "https://www.youtube.com/watch?v=W6Mm8Sbe__o",
                "awards": ["Academy Award for Best Picture", "Academy Award for Best Actor", "Academy Award for Best Actress"],
                "details": {"imdb_rating": 8.6, "psychological_thriller": True}
            },
            {
                "title": "Star Wars: Episode IV - A New Hope",
                "description": "Luke Skywalker joins forces with a Jedi Knight, a cocky pilot, a Wookiee and two droids to save the galaxy from the Empire's world-destroying battle station.",
                "duration_minutes": 121,
                "genre": ["Action", "Adventure", "Fantasy", "Sci-Fi"],
                "rating": "PG",
                "cast": ["Mark Hamill", "Harrison Ford", "Carrie Fisher", "Peter Cushing"],
                "director": "George Lucas",
                "writers": ["George Lucas"],
                "producers": ["Gary Kurtz"],
                "release_date": date(1977, 5, 25),
                "country": "USA",
                "language": "English",
                "budget": 11000000,
                "revenue": 775398007,
                "production_company": "Lucasfilm Ltd.",
                "distributor": "20th Century Fox",
                "image_url": "https://image.tmdb.org/t/p/w500/6FfCtAuVAW8XJjZ7eWeLibRLWTw.jpg",
                "trailer_url": "https://www.youtube.com/watch?v=1g3_CFmnU7k",
                "awards": ["Academy Award for Best Visual Effects", "Academy Award for Best Art Direction"],
                "details": {"imdb_rating": 8.6, "space_opera": True}
            },
            {
                "title": "Back to the Future",
                "description": "Marty McFly, a 17-year-old high school student, is accidentally sent thirty years into the past in a time-traveling DeLorean invented by his close friend, the eccentric scientist Doc Brown.",
                "duration_minutes": 116,
                "genre": ["Adventure", "Comedy", "Sci-Fi"],
                "rating": "PG",
                "cast": ["Michael J. Fox", "Christopher Lloyd", "Lea Thompson", "Crispin Glover"],
                "director": "Robert Zemeckis",
                "writers": ["Robert Zemeckis", "Bob Gale"],
                "producers": ["Neil Canton", "Bob Gale"],
                "release_date": date(1985, 7, 3),
                "country": "USA",
                "language": "English",
                "budget": 19000000,
                "revenue": 381109762,
                "production_company": "Universal Pictures",
                "distributor": "Universal Pictures",
                "image_url": "https://image.tmdb.org/t/p/w500/7lyBcpYB0Qt8gYhXYaEZUNlNQAv.jpg",
                "trailer_url": "https://www.youtube.com/watch?v=qvsgGtivCgs",
                "awards": ["Academy Award for Best Sound Effects Editing"],
                "details": {"imdb_rating": 8.5, "time_travel": True}
            },
            {
                "title": "The Terminator",
                "description": "A human soldier is sent from 2029 to 1984 to stop an almost indestructible cyborg killing machine, sent from the same year, which has been programmed to execute a young woman.",
                "duration_minutes": 107,
                "genre": ["Action", "Sci-Fi"],
                "rating": "R",
                "cast": ["Arnold Schwarzenegger", "Linda Hamilton", "Michael Biehn", "Paul Winfield"],
                "director": "James Cameron",
                "writers": ["James Cameron", "Gale Anne Hurd"],
                "producers": ["Gale Anne Hurd"],
                "release_date": date(1984, 10, 26),
                "country": "USA",
                "language": "English",
                "budget": 6400000,
                "revenue": 78371200,
                "production_company": "Hemdale Film Corporation",
                "distributor": "Orion Pictures",
                "image_url": "https://image.tmdb.org/t/p/w500/qvktm0BHcnmDpul4U47QzrH1M2H.jpg",
                "trailer_url": "https://www.youtube.com/watch?v=k64P4l2Wmeg",
                "awards": ["Nominated for Academy Award for Best Visual Effects"],
                "details": {"imdb_rating": 8.1, "cyberpunk": True}
            },
            {
                "title": "Toy Story",
                "description": "A cowboy doll is profoundly threatened and jealous when a new spaceman figure supplants him as top toy in a boy's room.",
                "duration_minutes": 81,
                "genre": ["Animation", "Adventure", "Comedy"],
                "rating": "G",
                "cast": ["Tom Hanks", "Tim Allen", "Don Rickles", "Jim Varney"],
                "director": "John Lasseter",
                "writers": ["John Lasseter", "Pete Docter", "Andrew Stanton"],
                "producers": ["Ralph Guggenheim", "Bonnie Arnold"],
                "release_date": date(1995, 11, 22),
                "country": "USA",
                "language": "English",
                "budget": 30000000,
                "revenue": 373554033,
                "production_company": "Pixar Animation Studios",
                "distributor": "Buena Vista Pictures",
                "image_url": "https://image.tmdb.org/t/p/w500/uXDfjJbdP4ijW5hWSBrPrlKpxab.jpg",
                "trailer_url": "https://www.youtube.com/watch?v=KYz2wyBy3kc",
                "awards": ["Academy Award for Best Original Song"],
                "details": {"imdb_rating": 8.3, "pixar_classic": True}
            },
            {
                "title": "Saving Private Ryan",
                "description": "Following the Normandy Landings, a group of U.S. soldiers go behind enemy lines to retrieve a paratrooper whose brothers have been killed in action.",
                "duration_minutes": 169,
                "genre": ["Drama", "War"],
                "rating": "R",
                "cast": ["Tom Hanks", "Matt Damon", "Tom Sizemore", "Edward Burns"],
                "director": "Steven Spielberg",
                "writers": ["Robert Rodat"],
                "producers": ["Steven Spielberg", "Ian Bryce", "Mark Gordon"],
                "release_date": date(1998, 7, 24),
                "country": "USA",
                "language": "English",
                "budget": 70000000,
                "revenue": 481840909,
                "production_company": "DreamWorks Pictures",
                "distributor": "Paramount Pictures",
                "image_url": "https://image.tmdb.org/t/p/w500/1wY4psJ5NVEhCuOYROGsXQ98Llq.jpg",
                "trailer_url": "https://www.youtube.com/watch?v=zwhP5b4tD6g",
                "awards": ["Academy Award for Best Director", "Academy Award for Best Cinematography"],
                "details": {"imdb_rating": 8.6, "world_war_ii": True}
            },
            {
                "title": "The Usual Suspects",
                "description": "A sole survivor tells of the twisty events leading up to a horrific gun battle on a boat, which began when five criminals met at a seemingly random police lineup.",
                "duration_minutes": 106,
                "genre": ["Crime", "Drama", "Mystery"],
                "rating": "R",
                "cast": ["Kevin Spacey", "Gabriel Byrne", "Benicio del Toro", "Kevin Pollak"],
                "director": "Bryan Singer",
                "writers": ["Christopher McQuarrie"],
                "producers": ["Michael McDonnell", "Bryan Singer"],
                "release_date": date(1995, 8, 16),
                "country": "USA",
                "language": "English",
                "budget": 6000000,
                "revenue": 23341568,
                "production_company": "Bad Hat Harry Productions",
                "distributor": "Gramercy Pictures",
                "image_url": "https://image.tmdb.org/t/p/w500/9nwL2JdDcO6s3dc5Nd1zSn9eEwA.jpg",
                "trailer_url": "https://www.youtube.com/watch?v=oiXdPolca5w",
                "awards": ["Academy Award for Best Supporting Actor"],
                "details": {"imdb_rating": 8.5, "twist_ending": True}
            },
            {
                "title": "Braveheart",
                "description": "Scottish warrior William Wallace leads his countrymen in a rebellion to free his homeland from the tyranny of King Edward I of England.",
                "duration_minutes": 178,
                "genre": ["Biography", "Drama", "History", "War"],
                "rating": "R",
                "cast": ["Mel Gibson", "Sophie Marceau", "Patrick McGoohan", "Angus Macfadyen"],
                "director": "Mel Gibson",
                "writers": ["Randall Wallace"],
                "producers": ["Mel Gibson", "Alan Ladd Jr.", "Bruce Davey"],
                "release_date": date(1995, 5, 24),
                "country": "USA",
                "language": "English",
                "budget": 72000000,
                "revenue": 210409989,
                "production_company": "Paramount Pictures",
                "distributor": "Paramount Pictures",
                "image_url": "https://image.tmdb.org/t/p/w500/or1gBugWhfjKpFj3JGrpfxKdEf0.jpg",
                "trailer_url": "https://www.youtube.com/watch?v=1NJO0jxBtMo",
                "awards": ["Academy Award for Best Picture", "Academy Award for Best Director"],
                "details": {"imdb_rating": 8.3, "historical_drama": True}
            },
            # Coming Soon Movies (with future release dates - no showtimes)
            {
                "title": "Dune: Part Two",
                "description": "Paul Atreides unites with Chani and the Fremen while on a path of revenge against the conspirators who destroyed his family.",
                "duration_minutes": 166,
                "genre": ["Action", "Adventure", "Drama", "Sci-Fi"],
                "rating": "PG-13",
                "cast": ["Timothée Chalamet", "Zendaya", "Rebecca Ferguson", "Javier Bardem"],
                "director": "Denis Villeneuve",
                "writers": ["Denis Villeneuve", "Jon Spaihts"],
                "producers": ["Mary Parent", "Cale Boyter"],
                "release_date": date(2024, 3, 1),
                "country": "USA",
                "language": "English",
                "budget": 190000000,
                "revenue": 711844037,
                "production_company": "Warner Bros. Pictures",
                "distributor": "Warner Bros. Pictures",
                "image_url": "https://image.tmdb.org/t/p/w500/1pdfLvkbY9ohJlCjQH2CZjjYVvJ.jpg",
                "trailer_url": "https://www.youtube.com/watch?v=Way9Dexny3w",
                "awards": [],
                "details": {"sequel": True, "based_on_frank_herbert": True}
            },
            {
                "title": "Avatar: The Way of Water",
                "description": "Jake Sully lives with his newfound family formed on the extrasolar moon Pandora. Once a familiar threat returns to finish what was previously started.",
                "duration_minutes": 192,
                "genre": ["Action", "Adventure", "Fantasy", "Sci-Fi"],
                "rating": "PG-13",
                "cast": ["Sam Worthington", "Zoe Saldana", "Sigourney Weaver", "Stephen Lang"],
                "director": "James Cameron",
                "writers": ["James Cameron", "Rick Jaffa", "Amanda Silver"],
                "producers": ["James Cameron", "Jon Landau"],
                "release_date": date(2022, 12, 16),
                "country": "USA",
                "language": "English",
                "budget": 350000000,
                "revenue": 2320250281,
                "production_company": "20th Century Studios",
                "distributor": "20th Century Studios",
                "image_url": "https://image.tmdb.org/t/p/w500/t6HIqrRAclMCA60NsSmeqe9RmNV.jpg",
                "trailer_url": "https://www.youtube.com/watch?v=d9MyW72ELq0",
                "awards": ["Academy Award for Best Visual Effects"],
                "details": {"highest_grossing": True, "sequel": True}
            },
            {
                "title": "Oppenheimer",
                "description": "The story of American scientist J. Robert Oppenheimer and his role in the development of the atomic bomb.",
                "duration_minutes": 180,
                "genre": ["Biography", "Drama", "History"],
                "rating": "R",
                "cast": ["Cillian Murphy", "Emily Blunt", "Matt Damon", "Robert Downey Jr."],
                "director": "Christopher Nolan",
                "writers": ["Christopher Nolan"],
                "producers": ["Emma Thomas", "Charles Roven"],
                "release_date": date(2023, 8, 11),
                "country": "USA",
                "language": "English",
                "budget": 100000000,
                "revenue": 952000000,
                "production_company": "Universal Pictures",
                "distributor": "Universal Pictures",
                "image_url": "https://image.tmdb.org/t/p/w500/8Gxv8gSFCU0XGDykEGv7zR1n2ua.jpg",
                "trailer_url": "https://www.youtube.com/watch?v=uYPbbksJxIg",
                "awards": ["Academy Award for Best Picture", "Academy Award for Best Director"],
                "details": {"biographical": True, "historical": True}
            },
            {
                "title": "Barbie",
                "description": "Barbie and Ken are having the time of their lives in the colorful and seemingly perfect world of Barbie Land. However, when they get a chance to go to the real world, they soon discover the joys and perils of living among humans.",
                "duration_minutes": 114,
                "genre": ["Adventure", "Comedy", "Fantasy"],
                "rating": "PG-13",
                "cast": ["Margot Robbie", "Ryan Gosling", "Issa Rae", "Kate McKinnon"],
                "director": "Greta Gerwig",
                "writers": ["Greta Gerwig", "Noah Baumbach"],
                "producers": ["David Heyman", "Margot Robbie", "Tom Ackerley"],
                "release_date": date(2023, 7, 21),
                "country": "USA",
                "language": "English",
                "budget": 145000000,
                "revenue": 1440000000,
                "production_company": "Warner Bros. Pictures",
                "distributor": "Warner Bros. Pictures",
                "image_url": "https://image.tmdb.org/t/p/w500/iuFNMS8U5cb6xfzi51Dbkovj7vM.jpg",
                "trailer_url": "https://www.youtube.com/watch?v=pBk4NYhWNMM",
                "awards": ["Academy Award for Best Original Song"],
                "details": {"highest_grossing_2023": True, "satirical": True}
            },
            {
                "title": "Guardians of the Galaxy Vol. 3",
                "description": "Peter Quill, still reeling from the loss of Gamora, must rally his team around him to defend the universe along with protecting one of their own.",
                "duration_minutes": 150,
                "genre": ["Action", "Adventure", "Comedy", "Sci-Fi"],
                "rating": "PG-13",
                "cast": ["Chris Pratt", "Zoe Saldana", "Dave Bautista", "Karen Gillan"],
                "director": "James Gunn",
                "writers": ["James Gunn"],
                "producers": ["Kevin Feige"],
                "release_date": date(2023, 5, 5),
                "country": "USA",
                "language": "English",
                "budget": 250000000,
                "revenue": 845555777,
                "production_company": "Marvel Studios",
                "distributor": "Walt Disney Studios Motion Pictures",
                "image_url": "https://image.tmdb.org/t/p/w500/r2J02Z2OpNTctfOSN1Ydgii51I3.jpg",
                "trailer_url": "https://www.youtube.com/watch?v=u3V5KDHRQvk",
                "awards": [],
                "details": {"marvel_cinematic_universe": True, "finale": True}
            },
            {
                "title": "Spider-Man: Across the Spider-Verse",
                "description": "After reuniting with Gwen Stacy, Miles Morales finds himself catapulted across the Multiverse, where he encounters a team of Spider-People charged with protecting its very existence.",
                "duration_minutes": 140,
                "genre": ["Animation", "Action", "Adventure"],
                "rating": "PG",
                "cast": ["Shameik Moore", "Hailee Steinfeld", "Brian Tyree Henry", "Luna Lauren Velez"],
                "director": "Joaquim Dos Santos",
                "writers": ["Phil Lord", "Christopher Miller", "David Callaham"],
                "producers": ["Avi Arad", "Amy Pascal", "Phil Lord"],
                "release_date": date(2023, 6, 2),
                "country": "USA",
                "language": "English",
                "budget": 100000000,
                "revenue": 690515087,
                "production_company": "Columbia Pictures",
                "distributor": "Sony Pictures Releasing",
                "image_url": "https://image.tmdb.org/t/p/w500/8Vt6mWEReuy4Of61Lnj5Xj704m8.jpg",
                "trailer_url": "https://www.youtube.com/watch?v=cqGjhVJWtEg",
                "awards": ["Academy Award for Best Animated Feature"],
                "details": {"animated": True, "multiverse": True}
            },
            {
                "title": "John Wick: Chapter 4",
                "description": "With the price on his head ever increasing, John Wick uncovers a path to defeating The High Table. But before he can earn his freedom, Wick must face off against a new enemy.",
                "duration_minutes": 169,
                "genre": ["Action", "Crime", "Thriller"],
                "rating": "R",
                "cast": ["Keanu Reeves", "Laurence Fishburne", "George Georgiou", "Lance Reddick"],
                "director": "Chad Stahelski",
                "writers": ["Shay Hatten", "Michael Finch"],
                "producers": ["Basil Iwanyk", "Erica Lee"],
                "release_date": date(2023, 3, 24),
                "country": "USA",
                "language": "English",
                "budget": 90000000,
                "revenue": 440157693,
                "production_company": "Thunder Road Pictures",
                "distributor": "Lionsgate",
                "image_url": "https://image.tmdb.org/t/p/w500/vZloFAK7NmvMGKE7VkF5UHaz0I.jpg",
                "trailer_url": "https://www.youtube.com/watch?v=qEVUtrk8_B4",
                "awards": [],
                "details": {"action_franchise": True, "finale": True}
            },
            {
                "title": "Mission: Impossible - Dead Reckoning Part One",
                "description": "Ethan Hunt and his IMF team must track down a dangerous weapon before it falls into the wrong hands.",
                "duration_minutes": 163,
                "genre": ["Action", "Adventure", "Thriller"],
                "rating": "PG-13",
                "cast": ["Tom Cruise", "Hayley Atwell", "Ving Rhames", "Simon Pegg"],
                "director": "Christopher McQuarrie",
                "writers": ["Christopher McQuarrie", "Erik Jendresen"],
                "producers": ["Tom Cruise", "Christopher McQuarrie"],
                "release_date": date(2023, 7, 12),
                "country": "USA",
                "language": "English",
                "budget": 291000000,
                "revenue": 567535383,
                "production_company": "Paramount Pictures",
                "distributor": "Paramount Pictures",
                "image_url": "https://image.tmdb.org/t/p/w500/NNxYkU70HPurnNCSiCjYdd9hzW.jpg",
                "trailer_url": "https://www.youtube.com/watch?v=avz06PDqDbM",
                "awards": [],
                "details": {"action_franchise": True, "high_budget": True}
            },
            {
                "title": "The Batman",
                "description": "When a sadistic serial killer begins murdering key political figures in Gotham, Batman is forced to investigate the city's hidden corruption.",
                "duration_minutes": 176,
                "genre": ["Action", "Crime", "Drama", "Thriller"],
                "rating": "PG-13",
                "cast": ["Robert Pattinson", "Zoë Kravitz", "Jeffrey Wright", "Colin Farrell"],
                "director": "Matt Reeves",
                "writers": ["Matt Reeves", "Peter Craig"],
                "producers": ["Matt Reeves", "Dylan Clark"],
                "release_date": date(2022, 3, 4),
                "country": "USA",
                "language": "English",
                "budget": 185000000,
                "revenue": 770836163,
                "production_company": "Warner Bros. Pictures",
                "distributor": "Warner Bros. Pictures",
                "image_url": "https://image.tmdb.org/t/p/w500/74xTEgt7R36Fpooo50r9T25onhq.jpg",
                "trailer_url": "https://www.youtube.com/watch?v=mqqft2x_Aa4",
                "awards": ["Academy Award for Best Cinematography"],
                "details": {"dark_knight": True, "reboot": True}
            },
            {
                "title": "Top Gun: Maverick",
                "description": "After thirty years, Maverick is still pushing the envelope as a top naval aviator, but must confront ghosts of his past when he leads TOP GUN's elite graduates on a mission that demands the ultimate sacrifice.",
                "duration_minutes": 130,
                "genre": ["Action", "Drama"],
                "rating": "PG-13",
                "cast": ["Tom Cruise", "Miles Teller", "Jennifer Connelly", "Jon Hamm"],
                "director": "Joseph Kosinski",
                "writers": ["Ehren Kruger", "Eric Warren Singer", "Christopher McQuarrie"],
                "producers": ["Tom Cruise", "Christopher McQuarrie", "David Ellison"],
                "release_date": date(2022, 5, 27),
                "country": "USA",
                "language": "English",
                "budget": 170000000,
                "revenue": 1488732821,
                "production_company": "Paramount Pictures",
                "distributor": "Paramount Pictures",
                "image_url": "https://image.tmdb.org/t/p/w500/62HCnUTziyWcpDaBO2i1DX17ljH.jpg",
                "trailer_url": "https://www.youtube.com/watch?v=qSqVVswa420",
                "awards": ["Academy Award for Best Sound"],
                "details": {"sequel": True, "highest_grossing_2022": True}
            },
            {
                "title": "Everything Everywhere All at Once",
                "description": "A middle-aged Chinese immigrant is swept up into an insane adventure in which she alone can save existence by exploring other universes and connecting with the lives she could have lived.",
                "duration_minutes": 139,
                "genre": ["Action", "Adventure", "Comedy", "Sci-Fi"],
                "rating": "R",
                "cast": ["Michelle Yeoh", "Stephanie Hsu", "Ke Huy Quan", "Jamie Lee Curtis"],
                "director": "Daniels",
                "writers": ["Daniels"],
                "producers": ["Anthony Russo", "Joe Russo"],
                "release_date": date(2022, 4, 8),
                "country": "USA",
                "language": "English",
                "budget": 25000000,
                "revenue": 103000000,
                "production_company": "A24",
                "distributor": "A24",
                "image_url": "https://image.tmdb.org/t/p/w500/w3LxiVYdWWRvEVdn5RYq6jIqkb1.jpg",
                "trailer_url": "https://www.youtube.com/watch?v=wxN1T1uxQ2g",
                "awards": ["Academy Award for Best Picture", "Academy Award for Best Director"],
                "details": {"multiverse": True, "indie_hit": True}
            },
            # More Coming Soon Movies (2024-2026 releases)
            {
                "title": "Furiosa: A Mad Max Saga",
                "description": "The origin story of renegade warrior Furiosa before her encounter and team up with Max Rockatansky.",
                "duration_minutes": 148,
                "genre": ["Action", "Adventure", "Sci-Fi"],
                "rating": "R",
                "cast": ["Anya Taylor-Joy", "Chris Hemsworth", "Tom Burke", "Nathan Jones"],
                "director": "George Miller",
                "writers": ["George Miller", "Nick Lathouris"],
                "producers": ["George Miller", "Doug Mitchell"],
                "release_date": date(2024, 5, 24),
                "country": "Australia",
                "language": "English",
                "budget": 168000000,
                "revenue": 0,  # Not released yet
                "production_company": "Warner Bros. Pictures",
                "distributor": "Warner Bros. Pictures",
                "image_url": "https://image.tmdb.org/t/p/w500/iADOJ8Zymht2JPMoy3R7xceZprc.jpg",
                "trailer_url": "https://www.youtube.com/watch?v=XJMuhwVlca4",
                "awards": [],
                "details": {"prequel": True, "mad_max_universe": True}
            },
            {
                "title": "Kingdom of the Planet of the Apes",
                "description": "Many years after the reign of Caesar, a young ape goes on a journey that will lead him to question everything he's been taught about the past.",
                "duration_minutes": 145,
                "genre": ["Action", "Adventure", "Drama", "Sci-Fi"],
                "rating": "PG-13",
                "cast": ["Owen Teague", "Freya Allan", "Kevin Durand", "Peter Macon"],
                "director": "Wes Ball",
                "writers": ["Josh Friedman", "Rick Jaffa", "Amanda Silver"],
                "producers": ["Rick Jaffa", "Amanda Silver", "Jason Reed"],
                "release_date": date(2024, 5, 10),
                "country": "USA",
                "language": "English",
                "budget": 160000000,
                "revenue": 0,  # Not released yet
                "production_company": "20th Century Studios",
                "distributor": "20th Century Studios",
                "image_url": "https://image.tmdb.org/t/p/w500/gKkl37BQuKT5XQRhDbtzgUbE3FK.jpg",
                "trailer_url": "https://www.youtube.com/watch?v=Dz_cJV3WxO4",
                "awards": [],
                "details": {"sequel": True, "ape_saga": True}
            },
            {
                "title": "Deadpool & Wolverine",
                "description": "Deadpool is offered a place in the Marvel Cinematic Universe by the Time Variance Authority, but instead recruits a variant of Wolverine to save his universe from extinction.",
                "duration_minutes": 127,
                "genre": ["Action", "Comedy", "Sci-Fi"],
                "rating": "R",
                "cast": ["Ryan Reynolds", "Hugh Jackman", "Emma Corrin", "Morena Baccarin"],
                "director": "Shawn Levy",
                "writers": ["Ryan Reynolds", "Rhett Reese", "Paul Wernick"],
                "producers": ["Ryan Reynolds", "Lauren Shuler Donner"],
                "release_date": date(2024, 7, 26),
                "country": "USA",
                "language": "English",
                "budget": 200000000,
                "revenue": 0,  # Not released yet
                "production_company": "Marvel Studios",
                "distributor": "Walt Disney Studios Motion Pictures",
                "image_url": "https://image.tmdb.org/t/p/w500/8cdWjvZQUExUUTzyp4t6EDMubmR.jpg",
                "trailer_url": "https://www.youtube.com/watch?v=73_1biulkYk",
                "awards": [],
                "details": {"crossover": True, "marvel_cinematic_universe": True}
            },
            {
                "title": "Joker: Folie à Deux",
                "description": "Arthur Fleck, having been released from Arkham Asylum, forms a bond with Harley Quinn and their dangerous romance blossoms.",
                "duration_minutes": 138,
                "genre": ["Crime", "Drama", "Thriller"],
                "rating": "R",
                "cast": ["Joaquin Phoenix", "Lady Gaga", "Brendan Gleeson", "Catherine Keener"],
                "director": "Todd Phillips",
                "writers": ["Todd Phillips", "Scott Silver"],
                "producers": ["Todd Phillips", "Bradley Cooper"],
                "release_date": date(2024, 10, 4),
                "country": "USA",
                "language": "English",
                "budget": 200000000,
                "revenue": 0,  # Not released yet
                "production_company": "Warner Bros. Pictures",
                "distributor": "Warner Bros. Pictures",
                "image_url": "https://image.tmdb.org/t/p/w500/if8QiqCI7WAGImKcJCfzp6VTyKA.jpg",
                "trailer_url": "https://www.youtube.com/watch?v=_OKAwz2MsJs",
                "awards": [],
                "details": {"sequel": True, "musical_elements": True}
            },
            {
                "title": "Wicked",
                "description": "The untold story of the Witches of Oz, which follows Elphaba before her extraordinary transformation into the Wicked Witch of the West.",
                "duration_minutes": 160,
                "genre": ["Adventure", "Family", "Fantasy", "Musical"],
                "rating": "PG",
                "cast": ["Cynthia Erivo", "Ariana Grande", "Michelle Yeoh", "Jeff Goldblum"],
                "director": "Jon M. Chu",
                "writers": ["Winnie Holzman"],
                "producers": ["Marc Platt"],
                "release_date": date(2024, 11, 22),
                "country": "USA",
                "language": "English",
                "budget": 300000000,
                "revenue": 0,  # Not released yet
                "production_company": "Universal Pictures",
                "distributor": "Universal Pictures",
                "image_url": "https://image.tmdb.org/t/p/w500/xDGbZ0JJ3mYaGKy4Nzd9KphxA8.jpg",
                "trailer_url": "https://www.youtube.com/watch?v=6COmYeLsz4c",
                "awards": [],
                "details": {"musical": True, "based_on_broadway": True}
            },
            {
                "title": "Gladiator II",
                "description": "Years after witnessing the death of the revered hero Maximus at the hands of his uncle, Lucius is forced to enter the Colosseum after his home is conquered by the tyrannical Emperors.",
                "duration_minutes": 148,
                "genre": ["Action", "Adventure", "Drama"],
                "rating": "R",
                "cast": ["Denzel Washington", "Pedro Pascal", "Lior Raz", "May Calamawy"],
                "director": "Ridley Scott",
                "writers": ["David Scarpa"],
                "producers": ["Ridley Scott", "Michael Pruss", "Gianni Nunnari"],
                "release_date": date(2025, 11, 14),
                "country": "USA",
                "language": "English",
                "budget": 250000000,
                "revenue": 0,  # Not released yet
                "production_company": "Paramount Pictures",
                "distributor": "Paramount Pictures",
                "image_url": "https://image.tmdb.org/t/p/w500/2cxhvwyEwRlysAmRH4IODkvo0z5.jpg",
                "trailer_url": "https://www.youtube.com/watch?v=4rgYUipGJNo",
                "awards": [],
                "details": {"sequel": True, "historical_drama": True}
            },
            {
                "title": "Avengers: Doomsday",
                "description": "The Avengers assemble once more to face their greatest threat yet - the return of Doomsday.",
                "duration_minutes": 150,
                "genre": ["Action", "Adventure", "Sci-Fi"],
                "rating": "PG-13",
                "cast": ["Robert Downey Jr.", "Chris Evans", "Chris Hemsworth", "Scarlett Johansson"],
                "director": "Joss Whedon",
                "writers": ["Joss Whedon"],
                "producers": ["Kevin Feige"],
                "release_date": date(2026, 5, 1),
                "country": "USA",
                "language": "English",
                "budget": 400000000,
                "revenue": 0,  # Not released yet
                "production_company": "Marvel Studios",
                "distributor": "Walt Disney Studios Motion Pictures",
                "image_url": "https://image.tmdb.org/t/p/w500/9GBhzXMFjgcZ3FdR9w3bUMMTps5.jpg",
                "trailer_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",  # Placeholder
                "awards": [],
                "details": {"marvel_cinematic_universe": True, "epic_battle": True}
            },
            {
                "title": "Star Wars: Episode X - The Rise of Skywalker",
                "description": "The surviving members of the resistance face the First Order once again in the final chapter of the Skywalker saga.",
                "duration_minutes": 142,
                "genre": ["Action", "Adventure", "Fantasy", "Sci-Fi"],
                "rating": "PG-13",
                "cast": ["Daisy Ridley", "Adam Driver", "John Boyega", "Oscar Isaac"],
                "director": "J.J. Abrams",
                "writers": ["Chris Terrio", "J.J. Abrams"],
                "producers": ["Kathleen Kennedy", "J.J. Abrams", "Michelle Rejwan"],
                "release_date": date(2019, 12, 20),
                "country": "USA",
                "language": "English",
                "budget": 275000000,
                "revenue": 1074144248,
                "production_company": "Lucasfilm Ltd.",
                "distributor": "Walt Disney Studios Motion Pictures",
                "image_url": "https://image.tmdb.org/t/p/w500/db32LaOibwEliAmSL2jjDF6oDdj.jpg",
                "trailer_url": "https://www.youtube.com/watch?v=8Qn_spdM5Zg",
                "awards": [],
                "details": {"saga_finale": True, "space_opera": True}
            },
            {
                "title": "Avatar 3",
                "description": "The continuation of Jake and Neytiri's story as they explore new worlds and face new challenges.",
                "duration_minutes": 190,
                "genre": ["Action", "Adventure", "Sci-Fi"],
                "rating": "PG-13",
                "cast": ["Sam Worthington", "Zoe Saldana", "Sigourney Weaver", "Stephen Lang"],
                "director": "James Cameron",
                "writers": ["James Cameron", "Rick Jaffa", "Amanda Silver"],
                "producers": ["James Cameron", "Jon Landau"],
                "release_date": date(2025, 12, 19),
                "country": "USA",
                "language": "English",
                "budget": 350000000,
                "revenue": 0,
                "production_company": "20th Century Studios",
                "distributor": "20th Century Studios",
                "image_url": "https://image.tmdb.org/t/p/w500/avatar3_placeholder.jpg",
                "trailer_url": "https://www.youtube.com/watch?v=coming_soon",
                "awards": [],
                "details": {"franchise": "Avatar", "part": 3}
            },
            {
                "title": "Marvel's Fantastic Four",
                "description": "The first family of Marvel Comics gets their MCU debut in this highly anticipated film.",
                "duration_minutes": 145,
                "genre": ["Action", "Adventure", "Sci-Fi", "Superhero"],
                "rating": "PG-13",
                "cast": ["Pedro Pascal", "Vanessa Kirby", "Joseph Quinn", "Ebon Moss-Bachrach"],
                "director": "Matt Shakman",
                "writers": ["Josh Friedman", "Cameron Squires"],
                "producers": ["Kevin Feige", "Grant Curtis"],
                "release_date": date(2025, 7, 25),
                "country": "USA",
                "language": "English",
                "budget": 200000000,
                "revenue": 0,
                "production_company": "Marvel Studios",
                "distributor": "Walt Disney Studios Motion Pictures",
                "image_url": "https://image.tmdb.org/t/p/w500/fantastic_four_placeholder.jpg",
                "trailer_url": "https://www.youtube.com/watch?v=coming_soon",
                "awards": [],
                "details": {"marvel_cinematic_universe": True, "first_family": True}
            },
            {
                "title": "Superman: Legacy",
                "description": "The next chapter in DC's cinematic universe featuring a younger Superman for a new generation.",
                "duration_minutes": 140,
                "genre": ["Action", "Adventure", "Sci-Fi", "Superhero"],
                "rating": "PG-13",
                "cast": ["David Corenswet", "Rachel Brosnahan", "Nicholas Hoult", "Edi Gathegi"],
                "director": "James Gunn",
                "writers": ["James Gunn"],
                "producers": ["James Gunn", "Peter Safran"],
                "release_date": date(2025, 7, 11),
                "country": "USA",
                "language": "English",
                "budget": 250000000,
                "revenue": 0,
                "production_company": "DC Studios",
                "distributor": "Warner Bros. Pictures",
                "image_url": "https://image.tmdb.org/t/p/w500/superman_legacy_placeholder.jpg",
                "trailer_url": "https://www.youtube.com/watch?v=coming_soon",
                "awards": [],
                "details": {"dc_universe": True, "reboot": True}
            },
            # Add more SHOWING movies (recent releases within 90 days)
            {
                "title": "Fast X",
                "description": "Dom Toretto and his family must confront the most lethal opponent they've ever faced.",
                "duration_minutes": 141,
                "genre": ["Action", "Adventure", "Crime"],
                "rating": "PG-13",
                "cast": ["Vin Diesel", "Michelle Rodriguez", "Tyrese Gibson", "Ludacris"],
                "director": "Louis Leterrier",
                "writers": ["Justin Lin", "Dan Mazeau"],
                "producers": ["Neal H. Moritz", "Vin Diesel"],
                "release_date": date(2024, 11, 15),  # Recent date to be SHOWING
                "country": "USA",
                "language": "English",
                "budget": 340000000,
                "revenue": 714594726,
                "production_company": "Universal Pictures",
                "distributor": "Universal Pictures",
                "image_url": "https://image.tmdb.org/t/p/w500/fiVW06jE7z9YnO4trhaMEdclSiC.jpg",
                "trailer_url": "https://www.youtube.com/watch?v=32RAq6JzY-w",
                "awards": [],
                "details": {"franchise": "Fast & Furious", "action_packed": True}
            },
            {
                "title": "Indiana Jones and the Dial of Destiny",
                "description": "Harrison Ford returns as the legendary hero archaeologist in the highly anticipated fifth installment.",
                "duration_minutes": 154,
                "genre": ["Action", "Adventure"],
                "rating": "PG-13",
                "cast": ["Harrison Ford", "Phoebe Waller-Bridge", "Antonio Banderas", "Shaunette Renée Wilson"],
                "director": "James Mangold",
                "writers": ["Jez Butterworth", "John-Henry Butterworth"],
                "producers": ["Kathleen Kennedy", "Frank Marshall"],
                "release_date": date(2024, 11, 20),  # Recent date to be SHOWING
                "country": "USA",
                "language": "English",
                "budget": 295000000,
                "revenue": 384000000,
                "production_company": "Lucasfilm",
                "distributor": "Walt Disney Studios",
                "image_url": "https://image.tmdb.org/t/p/w500/Af4bXE63pVsb2FtbW8uYIyPBadD.jpg",
                "trailer_url": "https://www.youtube.com/watch?v=ZEuHX4Zu8vs",
                "awards": [],
                "details": {"franchise": "Indiana Jones", "final_ford_film": True}
            },
            {
                "title": "The Flash",
                "description": "Barry Allen uses his superpowers to travel back in time in order to change the events of the past.",
                "duration_minutes": 144,
                "genre": ["Action", "Adventure", "Sci-Fi"],
                "rating": "PG-13",
                "cast": ["Ezra Miller", "Sasha Calle", "Michael Shannon", "Ron Livingston"],
                "director": "Andy Muschietti",
                "writers": ["Christina Hodson"],
                "producers": ["Barbara Muschietti", "Michael Disco"],
                "release_date": date(2024, 11, 25),  # Recent date to be SHOWING
                "country": "USA",
                "language": "English",
                "budget": 300000000,
                "revenue": 271000000,
                "production_company": "Warner Bros. Pictures",
                "distributor": "Warner Bros. Pictures",
                "image_url": "https://image.tmdb.org/t/p/w500/rktDFPbfHfUbArZ6OOOKsXcv0Bm.jpg",
                "trailer_url": "https://www.youtube.com/watch?v=hebWYacbdvc",
                "awards": [],
                "details": {"dc_universe": True, "multiverse": True}
            },
            {
                "title": "Transformers: Rise of the Beasts",
                "description": "A '90s globetrotting adventure that introduces the Maximals, Predacons, and Terrorcons to the existing battle on earth between Autobots and Decepticons.",
                "duration_minutes": 127,
                "genre": ["Action", "Adventure", "Sci-Fi"],
                "rating": "PG-13",
                "cast": ["Anthony Ramos", "Dominique Fishback", "Luna Lauren Velez", "Dean Scott Vazquez"],
                "director": "Steven Caple Jr.",
                "writers": ["Joby Harold", "Darnell Metayer"],
                "producers": ["Lorenzo di Bonaventura", "Tom DeSanto"],
                "release_date": date(2024, 11, 30),  # Recent date to be SHOWING
                "country": "USA",
                "language": "English",
                "budget": 200000000,
                "revenue": 438962038,
                "production_company": "Paramount Pictures",
                "distributor": "Paramount Pictures",
                "image_url": "https://image.tmdb.org/t/p/w500/gPbM0MK8CP8A174rmUwGsADNYKD.jpg",
                "trailer_url": "https://www.youtube.com/watch?v=WWU4ZhOiXCk",
                "awards": [],
                "details": {"franchise": "Transformers", "beast_wars": True}
            },
            {
                "title": "Wonka",
                "description": "The story will focus specifically on a young Willy Wonka and how he met the Oompa-Loompas on one of his earliest adventures.",
                "duration_minutes": 116,
                "genre": ["Adventure", "Comedy", "Family", "Fantasy", "Musical"],
                "rating": "PG",
                "cast": ["Timothée Chalamet", "Calah Lane", "Keegan-Michael Key", "Paterson Joseph"],
                "director": "Paul King",
                "writers": ["Simon Farnaby", "Paul King"],
                "producers": ["David Heyman"],
                "release_date": date(2024, 12, 5),  # Recent date to be SHOWING
                "country": "UK",
                "language": "English",
                "budget": 125000000,
                "revenue": 634000000,
                "production_company": "Warner Bros. Pictures",
                "distributor": "Warner Bros. Pictures",
                "image_url": "https://image.tmdb.org/t/p/w500/qhb1qOilapbapxWQn9jtRfQzrjq.jpg",
                "trailer_url": "https://www.youtube.com/watch?v=otNh9bTjXWg",
                "awards": [],
                "details": {"prequel": True, "musical": True}
            },
            {
                "title": "Aquaman and the Lost Kingdom",
                "description": "Arthur Curry must retrieve the legendary Trident of Atlan to save the underwater kingdom of Atlantis, and the world, from his half-brother Orm.",
                "duration_minutes": 124,
                "genre": ["Action", "Adventure", "Fantasy"],
                "rating": "PG-13",
                "cast": ["Jason Momoa", "Patrick Wilson", "Yahya Abdul-Mateen II", "Amber Heard"],
                "director": "James Wan",
                "writers": ["David Leslie Johnson-McGoldrick"],
                "producers": ["James Wan", "Peter Safran"],
                "release_date": date(2024, 12, 10),  # Recent date to be SHOWING
                "country": "USA",
                "language": "English",
                "budget": 215000000,
                "revenue": 435000000,
                "production_company": "Warner Bros. Pictures",
                "distributor": "Warner Bros. Pictures",
                "image_url": "https://image.tmdb.org/t/p/w500/7lTnXOy0iNtBAdRP3TZvaKb5Zg.jpg",
                "trailer_url": "https://www.youtube.com/watch?v=FV3bqvOHRQo",
                "awards": [],
                "details": {"sequel": True, "dc_universe": True}
            },
            {
                "title": "The Marvels",
                "description": "Carol Danvers, aka Captain Marvel, has reclaimed her identity from the tyrannical Kree.",
                "duration_minutes": 105,
                "genre": ["Action", "Adventure", "Sci-Fi"],
                "rating": "PG-13",
                "cast": ["Brie Larson", "Teyonah Parris", "Iman Vellani", "Samuel L. Jackson"],
                "director": "Nia DaCosta",
                "writers": ["Megan McDonnell", "Nia DaCosta"],
                "producers": ["Kevin Feige"],
                "release_date": date(2024, 12, 15),  # Recent date to be SHOWING
                "country": "USA",
                "language": "English",
                "budget": 274000000,
                "revenue": 206000000,
                "production_company": "Marvel Studios",
                "distributor": "Walt Disney Studios",
                "image_url": "https://image.tmdb.org/t/p/w500/9GBhzXMFjgcZ3FdR9w3bUMMTps5.jpg",
                "trailer_url": "https://www.youtube.com/watch?v=wS_qbDztgVY",
                "awards": [],
                "details": {"marvel_cinematic_universe": True, "team_up": True}
            },
            {
                "title": "Anyone But You",
                "description": "Two strangers hate each other but pretend to be a couple to attend a wedding in Australia.",
                "duration_minutes": 103,
                "genre": ["Comedy", "Romance"],
                "rating": "R",
                "cast": ["Sydney Sweeney", "Glen Powell", "Alexandra Shipp", "Hadley Robinson"],
                "director": "Will Gluck",
                "writers": ["Will Gluck", "Ilana Wolpert"],
                "producers": ["Will Gluck", "Joe Roth"],
                "release_date": date(2024, 12, 20),  # Recent date to be SHOWING
                "country": "USA",
                "language": "English",
                "budget": 25000000,
                "revenue": 220000000,
                "production_company": "Columbia Pictures",
                "distributor": "Sony Pictures",
                "image_url": "https://image.tmdb.org/t/p/w500/yRt7MGBElkLQOYRvLTT1b3B1rcp.jpg",
                "trailer_url": "https://www.youtube.com/watch?v=GQlbwgNEDyI",
                "awards": [],
                "details": {"romantic_comedy": True, "surprise_hit": True}
            }
        ]
        
        # Cast member details with image URLs
        cast_details = {
            # The Matrix
            "Keanu Reeves": "https://image.tmdb.org/t/p/w500/4D0PpNI0kmP58hgrwGC3wCjxhnm.jpg",
            "Laurence Fishburne": "https://image.tmdb.org/t/p/w500/8suEewj6DhVYlzJCXlLU5cVvo4g.jpg",
            "Carrie-Anne Moss": "https://image.tmdb.org/t/p/w500/xD4jTA3KmVp5Rq3aHcymL9DUGjD.jpg",
            "Hugo Weaving": "https://image.tmdb.org/t/p/w500/n5hRThNl67hKHmr2xePFkTEQDUF.jpg",
            
            # Inception
            "Leonardo DiCaprio": "https://image.tmdb.org/t/p/w500/wo2hJpn04vbtmh0B9utCFdsQhxM.jpg",
            "Joseph Gordon-Levitt": "https://image.tmdb.org/t/p/w500/z2FA8js799xqtfiFjBTicFYdfk.jpg",
            "Ellen Page": "https://image.tmdb.org/t/p/w500/eCeFgzS8N348ty6POB3vA1ZN0mw.jpg",
            "Tom Hardy": "https://image.tmdb.org/t/p/w500/d81K0RH8UX7tZj49tZaQhZ9ewH.jpg",
            "Marion Cotillard": "https://image.tmdb.org/t/p/w500/mZx1JFh4GsjAkx2MtWYKVhKLJ6n.jpg",
            
            # The Dark Knight
            "Christian Bale": "https://image.tmdb.org/t/p/w500/3qx2QFUbG6t6IlzR0F9k3Z6Yhf7.jpg",
            "Heath Ledger": "https://image.tmdb.org/t/p/w500/5Y9HnYYa9jF4NunY9lSgJGjSe8E.jpg",
            "Aaron Eckhart": "https://image.tmdb.org/t/p/w500/zLbjugWkNOh4A58M8FDOHPJfJ5V.jpg",
            "Michael Caine": "https://image.tmdb.org/t/p/w500/bVZRMlpjTAO2pJK6v90buFgVbSW.jpg",
            "Gary Oldman": "https://image.tmdb.org/t/p/w500/2v9FVVBUrrkW2m3QOcYkuhq9A6o.jpg",
            
            # Interstellar
            "Matthew McConaughey": "https://image.tmdb.org/t/p/w500/sY2mwpafcwqyYS1sOySu1MENDse.jpg",
            "Anne Hathaway": "https://image.tmdb.org/t/p/w500/9NSc5ykfBoaBcJlZ09QFp7b6r4A.jpg",
            "Jessica Chastain": "https://image.tmdb.org/t/p/w500/vOFrDeYXILnj747dOleaNh4jK3l.jpg",
            "Matt Damon": "https://image.tmdb.org/t/p/w500/7WHlU5rMmRNxfcskt9MW0RZTGMP.jpg",
            
            # Pulp Fiction
            "John Travolta": "https://image.tmdb.org/t/p/w500/9GVufE87MMIrSn0CbJFLudkALdL.jpg",
            "Samuel L. Jackson": "https://image.tmdb.org/t/p/w500/AiAYAqwpM5xmiFrAIeQvUXDCVvo.jpg",
            "Uma Thurman": "https://image.tmdb.org/t/p/w500/xdnstENLdWMPWt9qyhtf695L4t6.jpg",
            "Bruce Willis": "https://image.tmdb.org/t/p/w500/A1XBu3CffBpSK8HEIJM8q7Mn4lz.jpg",
            "Ving Rhames": "https://image.tmdb.org/t/p/w500/4gpLVNJJvIdD90CGq9FD641xQ3Z.jpg",
            
            # The Shawshank Redemption
            "Tim Robbins": "https://image.tmdb.org/t/p/w500/djT9FTXd4AJsBmEHGu2jqP3kBv4.jpg",
            "Morgan Freeman": "https://image.tmdb.org/t/p/w500/jPsLqiYGSofU4s6BjrxnefMfabb.jpg",
            "Bob Gunton": "https://image.tmdb.org/t/p/w500/2xq0MpLCQjzjsPWJYzVlN89zMiA.jpg",
            "William Sadler": "https://image.tmdb.org/t/p/w500/gAiL43Y4YhKuCjkT0PwlBAOKWj9.jpg",
            
            # Forrest Gump
            "Tom Hanks": "https://image.tmdb.org/t/p/w500/xndWFsBlClOJFRdhSt4NBwiPq2o.jpg",
            "Robin Wright": "https://image.tmdb.org/t/p/w500/4kH1K2vGpH8VsPWL17MJ8pqZ8Mn.jpg",
            "Gary Sinise": "https://image.tmdb.org/t/p/w500/7p1zLgSrgFbr04wQPBCqJDJHhmv.jpg",
            "Sally Field": "https://image.tmdb.org/t/p/w500/5FGVUlEJjjBOW4g4NVpVLs6u8s8.jpg",
            
            # The Godfather
            "Marlon Brando": "https://image.tmdb.org/t/p/w500/fuTEPMsBtV1zE98ujPONbKiYDc2.jpg",
            "Al Pacino": "https://image.tmdb.org/t/p/w500/2dGBb1fOcNdZjtQToVPFxXjm4ke.jpg",
            "James Caan": "https://image.tmdb.org/t/p/w500/lKTFLIRMIT4gQLd5lh7fZWpUJvQ.jpg",
            "Richard S. Castellano": "https://image.tmdb.org/t/p/w500/5wPOX8VlPCzaM8wjZFGbnKZjLpx.jpg",
            
            # Schindler's List
            "Liam Neeson": "https://image.tmdb.org/t/p/w500/bboldwqSC6tdw2iL6631c98l2Mn.jpg",
            "Ralph Fiennes": "https://image.tmdb.org/t/p/w500/tJr9n925VEbCIZntdSsuaB5MVy8.jpg",
            "Ben Kingsley": "https://image.tmdb.org/t/p/w500/vQtBqpF2HDdzbfXHDzR4u37i1Ac.jpg",
            "Caroline Goodall": "https://image.tmdb.org/t/p/w500/lMlXOZjmCtkHZtIaEGQSM5xDZ5O.jpg",
            
            # Fight Club
            "Brad Pitt": "https://image.tmdb.org/t/p/w500/ajNaPmXVVMJFg9GWmu6MJzTaXdV.jpg",
            "Edward Norton": "https://image.tmdb.org/t/p/w500/5XBzD5WuTyVQZeS4VI25z2moMeY.jpg",
            "Helena Bonham Carter": "https://image.tmdb.org/t/p/w500/DDeITcCpnBd0CkAIRPhggy9bt5.jpg",
            "Meat Loaf": "https://image.tmdb.org/t/p/w500/pwNyXgegO1nlZ8uWT847JM8EjGj.jpg",
            
            # The Lord of the Rings
            "Elijah Wood": "https://image.tmdb.org/t/p/w500/7UKRbJBNG7mxBl2QQc5XsAh9ulR.jpg",
            "Ian McKellen": "https://image.tmdb.org/t/p/w500/coWjgMEYJjk2OrNddlXCBm8EBct.jpg",
            "Orlando Bloom": "https://image.tmdb.org/t/p/w500/8jKF4i5lAYhTSPCMgAjIkQSXIbY.jpg",
            "Sean Bean": "https://image.tmdb.org/t/p/w500/kTjiABk3TJ3yI0Cto5RsvyT6V3o.jpg",
            
            # Gladiator
            "Russell Crowe": "https://image.tmdb.org/t/p/w500/uxiXuVH4vNWrKlJMVVPG1sxAJFe.jpg",
            "Joaquin Phoenix": "https://image.tmdb.org/t/p/w500/nXMzvVF6xR3OXOedozfLEbtc6Op.jpg",
            "Connie Nielsen": "https://image.tmdb.org/t/p/w500/lvQypTfeH2Gn2PTbzq6XkT2PLmn.jpg",
            "Oliver Reed": "https://image.tmdb.org/t/p/w500/6FduaQz5TaPzFl0x0WTPVF7zYO4.jpg",
            
            # Avatar
            "Sam Worthington": "https://image.tmdb.org/t/p/w500/i4FgJfPl3pDdFaeLgAVLtzfr7sL.jpg",
            "Zoe Saldana": "https://image.tmdb.org/t/p/w500/ofNrWiA2KDdqiNxFTLp51HcXUlp.jpg",
            "Sigourney Weaver": "https://image.tmdb.org/t/p/w500/flfhep27iBxseZIlxOMHt6zJFX1.jpg",
            "Stephen Lang": "https://image.tmdb.org/t/p/w500/vuAZGc6z0tmTu8UJm6r6w3cN0bx.jpg",
            
            # Titanic
            "Kate Winslet": "https://image.tmdb.org/t/p/w500/e3tdop3WhseRnn8KwMVLAV25Ybv.jpg",
            "Billy Zane": "https://image.tmdb.org/t/p/w500/vQSqH3ybDWZHZTqIemtnqqcrgqY.jpg",
            "Kathy Bates": "https://image.tmdb.org/t/p/w500/qZRTzTjV6wzvzFJJFnIjwtWF5YA.jpg",
            
            # The Green Mile
            "Michael Clarke Duncan": "https://image.tmdb.org/t/p/w500/7JVMS5f2sCMXMhK4RdYhfbO0iXE.jpg",
            "David Morse": "https://image.tmdb.org/t/p/w500/pDjuH4c9l6KQXFZALoRyVxLfLTq.jpg",
            "Bonnie Hunt": "https://image.tmdb.org/t/p/w500/shdQ6U7BTsCSuRUt5LKdMrUkuHa.jpg",
            
            # Parasite
            "Song Kang-ho": "https://image.tmdb.org/t/p/w500/jInMiHWKN3E1Tb9wPQYVwVlbay4.jpg",
            "Lee Sun-kyun": "https://image.tmdb.org/t/p/w500/2Hn5INcSIsZM7K6E7tTqyVKE94u.jpg",
            "Cho Yeo-jeong": "https://image.tmdb.org/t/p/w500/4YSd0s98duXWAYlZVnfUKwzh3Ij.jpg",
            "Choi Woo-shik": "https://image.tmdb.org/t/p/w500/4u5RJy7C8U6B0RdxTgJsWW6HlSR.jpg",
            
            # Additional Normal Movies Cast
            # The Lion King
            "Matthew Broderick": "https://image.tmdb.org/t/p/w500/9x7o2QJv2wJWQJ3oWQ5X3Q5Q5Q5.jpg",
            "Jeremy Irons": "https://image.tmdb.org/t/p/w500/2v9FVVBUrrkW2m3QOcYkuhq9A6o.jpg",
            "James Earl Jones": "https://image.tmdb.org/t/p/w500/oOhmKP2K3i7LCQ9O6eyG8Hd5gZ.jpg",
            "Whoopi Goldberg": "https://image.tmdb.org/t/p/w500/n3h5apHd7k4QOyJXK8NlQ9XcZ.jpg",
            
            # Jurassic Park
            "Sam Neill": "https://image.tmdb.org/t/p/w500/9pWo3Sv4dLM0G3k6wgX0QK7Q6Q.jpg",
            "Laura Dern": "https://image.tmdb.org/t/p/w500/4Q4Q4Q4Q4Q4Q4Q4Q4Q4Q4Q4Q4Q4Q.jpg",
            "Jeff Goldblum": "https://image.tmdb.org/t/p/w500/z2FA8js799xqtfiFjBTicFYdfk.jpg",
            "Richard Attenborough": "https://image.tmdb.org/t/p/w500/8Q8Q8Q8Q8Q8Q8Q8Q8Q8Q8Q8Q8Q8Q.jpg",
            
            # The Silence of the Lambs
            "Jodie Foster": "https://image.tmdb.org/t/p/w500/4D0PpNI0kmP58hgrwGC3wCjxhnm.jpg",
            "Anthony Hopkins": "https://image.tmdb.org/t/p/w500/9mdYwK2YcZNR8C5cGmYQ4Z9Z9Z.jpg",
            "Lawrence A. Bonney": "https://image.tmdb.org/t/p/w500/5wPOX8VlPCzaM8wjZFGbnKZjLpx.jpg",
            "Kasi Lemmons": "https://image.tmdb.org/t/p/w500/3qx2QFUbG6t6IlzR0F9k3Z6Yhf7.jpg",
            
            # Star Wars: Episode IV
            "Mark Hamill": "https://image.tmdb.org/t/p/w500/z2FA8js799xqtfiFjBTicFYdfk.jpg",
            "Harrison Ford": "https://image.tmdb.org/t/p/w500/7HiW0Rgdj6Kz9V0T0T0T0T0T0T0T.jpg",
            "Carrie Fisher": "https://image.tmdb.org/t/p/w500/e3tdop3WhseRnn8KwMVLAV25Ybv.jpg",
            "Peter Cushing": "https://image.tmdb.org/t/p/w500/2v9FVVBUrrkW2m3QOcYkuhq9A6o.jpg",
            
            # Back to the Future
            "Michael J. Fox": "https://image.tmdb.org/t/p/w500/7WHlU5rMmRNxfcskt9MW0RZTGMP.jpg",
            "Christopher Lloyd": "https://image.tmdb.org/t/p/w500/n5hRThNl67hKHmr2xePFkTEQDUF.jpg",
            "Lea Thompson": "https://image.tmdb.org/t/p/w500/4kH1K2vGpH8VsPWL17MJ8pqZ8Mn.jpg",
            "Crispin Glover": "https://image.tmdb.org/t/p/w500/5XBzD5WuTyVQZeS4VI25z2moMeY.jpg",
            
            # The Terminator
            "Arnold Schwarzenegger": "https://image.tmdb.org/t/p/w500/qJ2tW6WMUDux911r6m7haRef0WH.jpg",
            "Linda Hamilton": "https://image.tmdb.org/t/p/w500/9NSc5ykfBoaBcJlZ09QFp7b6r4A.jpg",
            "Michael Biehn": "https://image.tmdb.org/t/p/w500/d81K0RH8UX7tZj49tZaQhZ9ewH.jpg",
            "Paul Winfield": "https://image.tmdb.org/t/p/w500/2xq0MpLCQjzjsPWJYzVlN89zMiA.jpg",
            
            # Toy Story
            "Tom Hanks": "https://image.tmdb.org/t/p/w500/xndWFsBlClOJFRdhSt4NBwiPq2o.jpg",
            "Tim Allen": "https://image.tmdb.org/t/p/w500/d5iIlFn5s0ImszYzBPb8JPIfbXD.jpg",
            "Don Rickles": "https://image.tmdb.org/t/p/w500/gAiL43Y4YhKuCjkT0PwlBAOKWj9.jpg",
            "Jim Varney": "https://image.tmdb.org/t/p/w500/shdQ6U7BTsCSuRUt5LKdMrUkuHa.jpg",
            
            # Saving Private Ryan
            "Matt Damon": "https://image.tmdb.org/t/p/w500/7WHlU5rMmRNxfcskt9MW0RZTGMP.jpg",
            "Tom Sizemore": "https://image.tmdb.org/t/p/w500/5wPOX8VlPCzaM8wjZFGbnKZjLpx.jpg",
            "Edward Burns": "https://image.tmdb.org/t/p/w500/2v9FVVBUrrkW2m3QOcYkuhq9A6o.jpg",
            
            # The Usual Suspects
            "Kevin Spacey": "https://image.tmdb.org/t/p/w500/9mdYwK2YcZNR8C5cGmYQ4Z9Z9Z.jpg",
            "Gabriel Byrne": "https://image.tmdb.org/t/p/w500/2Hn5INcSIsZM7K6E7tTqyVKE94u.jpg",
            "Benicio del Toro": "https://image.tmdb.org/t/p/w500/kU3B75TyRiCgE270EyZnHjfivoq.jpg",
            "Kevin Pollak": "https://image.tmdb.org/t/p/w500/4u5RJy7C8U6B0RdxTgJsWW6HlSR.jpg",
            
            # Braveheart
            "Mel Gibson": "https://image.tmdb.org/t/p/w500/9x7o2QJv2wJWQJ3oWQ5X3Q5Q5Q5.jpg",
            "Sophie Marceau": "https://image.tmdb.org/t/p/w500/4YSd0s98duXWAYlZVnfUKwzh3Ij.jpg",
            "Patrick McGoohan": "https://image.tmdb.org/t/p/w500/2v9FVVBUrrkW2m3QOcYkuhq9A6o.jpg",
            "Angus Macfadyen": "https://image.tmdb.org/t/p/w500/5XBzD5WuTyVQZeS4VI25z2moMeY.jpg",
            
            # Coming Soon Movies Cast
            # Dune: Part Two
            "Timothée Chalamet": "https://image.tmdb.org/t/p/w500/BE2sdjpgsa2rNTFa66f7upkaOP.jpg",
            "Zendaya": "https://image.tmdb.org/t/p/w500/9u3Y4nlcQs2QGKkKwQDybN7hG.jpg",
            "Rebecca Ferguson": "https://image.tmdb.org/t/p/w500/lJloQh0UO7CVO5eSr1F3tcgw5w.jpg",
            "Javier Bardem": "https://image.tmdb.org/t/p/w500/fuTEPMsBtV1zE98ujPONbKiYDc2.jpg",
            
            # Avatar: The Way of Water
            "Sam Worthington": "https://image.tmdb.org/t/p/w500/i4FgJfPl3pDdFaeLgAVLtzfr7sL.jpg",
            "Zoe Saldana": "https://image.tmdb.org/t/p/w500/ofNrWiA2KDdqiNxFTLp51HcXUlp.jpg",
            "Sigourney Weaver": "https://image.tmdb.org/t/p/w500/flfhep27iBxseZIlxOMHt6zJFX1.jpg",
            "Stephen Lang": "https://image.tmdb.org/t/p/w500/vuAZGc6z0tmTu8UJm6r6w3cN0bx.jpg",
            
            # Oppenheimer
            "Cillian Murphy": "https://image.tmdb.org/t/p/w500/lldeQ91GwIVff43JBrpdbAAeYWj.jpg",
            "Emily Blunt": "https://image.tmdb.org/t/p/w500/9NSc5ykfBoaBcJlZ09QFp7b6r4A.jpg",
            "Matt Damon": "https://image.tmdb.org/t/p/w500/7WHlU5rMmRNxfcskt9MW0RZTGMP.jpg",
            "Robert Downey Jr.": "https://image.tmdb.org/t/p/w500/5qHNjhtjMD4YWH3UP0rm4tKwxCL.jpg",
            
            # Barbie
            "Margot Robbie": "https://image.tmdb.org/t/p/w500/euDPyqL7ju0sGQtZGx6S2bPn2p.jpg",
            "Ryan Gosling": "https://image.tmdb.org/t/p/w500/koEWntBv7JjQEVg0q8V9dPsDD.jpg",
            "Issa Rae": "https://image.tmdb.org/t/p/w500/8Q8Q8Q8Q8Q8Q8Q8Q8Q8Q8Q8Q8Q8Q.jpg",
            "Kate McKinnon": "https://image.tmdb.org/t/p/w500/xD4jTA3KmVp5Rq3aHcymL9DUGjD.jpg",
            
            # Guardians of the Galaxy Vol. 3
            "Chris Pratt": "https://image.tmdb.org/t/p/w500/83o3koL82jt30EJ0rz4Bnzrt2dd.jpg",
            "Zoe Saldana": "https://image.tmdb.org/t/p/w500/ofNrWiA2KDdqiNxFTLp51HcXUlp.jpg",
            "Dave Bautista": "https://image.tmdb.org/t/p/w500/ro3Qk3A6BgVCNjQF0H8fHVoC8j.jpg",
            "Karen Gillan": "https://image.tmdb.org/t/p/w500/9x7o2QJv2wJWQJ3oWQ5X3Q5Q5Q5.jpg",
            
            # Spider-Man: Across the Spider-Verse
            "Shameik Moore": "https://image.tmdb.org/t/p/w500/9x7o2QJv2wJWQJ3oWQ5X3Q5Q5Q5.jpg",
            "Hailee Steinfeld": "https://image.tmdb.org/t/p/w500/9NSc5ykfBoaBcJlZ09QFp7b6r4A.jpg",
            "Brian Tyree Henry": "https://image.tmdb.org/t/p/w500/5XBzD5WuTyVQZeS4VI25z2moMeY.jpg",
            "Luna Lauren Velez": "https://image.tmdb.org/t/p/w500/4YSd0s98duXWAYlZVnfUKwzh3Ij.jpg",
            
            # John Wick: Chapter 4
            "Keanu Reeves": "https://image.tmdb.org/t/p/w500/4D0PpNI0kmP58hgrwGC3wCjxhnm.jpg",
            "Laurence Fishburne": "https://image.tmdb.org/t/p/w500/8suEewj6DhVYlzJCXlLU5cVvo4g.jpg",
            "George Georgiou": "https://image.tmdb.org/t/p/w500/2v9FVVBUrrkW2m3QOcYkuhq9A6o.jpg",
            "Lance Reddick": "https://image.tmdb.org/t/p/w500/5wPOX8VlPCzaM8wjZFGbnKZjLpx.jpg",
            
            # Mission: Impossible - Dead Reckoning Part One
            "Tom Cruise": "https://image.tmdb.org/t/p/w500/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
            "Hayley Atwell": "https://image.tmdb.org/t/p/w500/9NSc5ykfBoaBcJlZ09QFp7b6r4A.jpg",
            "Ving Rhames": "https://image.tmdb.org/t/p/w500/4gpLVNJJvIdD90CGq9FD641xQ3Z.jpg",
            "Simon Pegg": "https://image.tmdb.org/t/p/w500/9x7o2QJv2wJWQJ3oWQ5X3Q5Q5Q5.jpg",
            
            # The Batman
            "Robert Pattinson": "https://image.tmdb.org/t/p/w500/kU3B75TyRiCgE270EyZnHjfivoq.jpg",
            "Zoë Kravitz": "https://image.tmdb.org/t/p/w500/9NSc5ykfBoaBcJlZ09QFp7b6r4A.jpg",
            "Jeffrey Wright": "https://image.tmdb.org/t/p/w500/2v9FVVBUrrkW2m3QOcYkuhq9A6o.jpg",
            "Colin Farrell": "https://image.tmdb.org/t/p/w500/kU3B75TyRiCgE270EyZnHjfivoq.jpg",
            
            # Top Gun: Maverick
            "Miles Teller": "https://image.tmdb.org/t/p/w500/9x7o2QJv2wJWQJ3oWQ5X3Q5Q5Q5.jpg",
            "Jennifer Connelly": "https://image.tmdb.org/t/p/w500/9NSc5ykfBoaBcJlZ09QFp7b6r4A.jpg",
            "Jon Hamm": "https://image.tmdb.org/t/p/w500/5XBzD5WuTyVQZeS4VI25z2moMeY.jpg",
            
            # Everything Everywhere All at Once
            "Michelle Yeoh": "https://image.tmdb.org/t/p/w500/9NSc5ykfBoaBcJlZ09QFp7b6r4A.jpg",
            "Stephanie Hsu": "https://image.tmdb.org/t/p/w500/4YSd0s98duXWAYlZVnfUKwzh3Ij.jpg",
            "Ke Huy Quan": "https://image.tmdb.org/t/p/w500/5wPOX8VlPCzaM8wjZFGbnKZjLpx.jpg",
            "Jamie Lee Curtis": "https://image.tmdb.org/t/p/w500/9x7o2QJv2wJWQJ3oWQ5X3Q5Q5Q5.jpg",
            
            # More Coming Soon Movies Cast
            # Furiosa: A Mad Max Saga
            "Anya Taylor-Joy": "https://image.tmdb.org/t/p/w500/jHwyl5lZjUwLfC7J5eW2L1f9z.jpg",
            "Chris Hemsworth": "https://image.tmdb.org/t/p/w500/2v9FVVBUrrkW2m3QOcYkuhq9A6o.jpg",
            "Tom Burke": "https://image.tmdb.org/t/p/w500/5XBzD5WuTyVQZeS4VI25z2moMeY.jpg",
            "Nathan Jones": "https://image.tmdb.org/t/p/w500/4u5RJy7C8U6B0RdxTgJsWW6HlSR.jpg",
            
            # Kingdom of the Planet of the Apes
            "Owen Teague": "https://image.tmdb.org/t/p/w500/9x7o2QJv2wJWQJ3oWQ5X3Q5Q5Q5.jpg",
            "Freya Allan": "https://image.tmdb.org/t/p/w500/4YSd0s98duXWAYlZVnfUKwzh3Ij.jpg",
            "Kevin Durand": "https://image.tmdb.org/t/p/w500/2v9FVVBUrrkW2m3QOcYkuhq9A6o.jpg",
            "Peter Macon": "https://image.tmdb.org/t/p/w500/5wPOX8VlPCzaM8wjZFGbnKZjLpx.jpg",
            
            # Deadpool & Wolverine
            "Ryan Reynolds": "https://image.tmdb.org/t/p/w500/4ynQYtSEuU5hyIPYx6GuLuE6p8H.jpg",
            "Hugh Jackman": "https://image.tmdb.org/t/p/w500/oAIDT5xbS3iG7s8nMfEo3n2iSz.jpg",
            "Emma Corrin": "https://image.tmdb.org/t/p/w500/9NSc5ykfBoaBcJlZ09QFp7b6r4A.jpg",
            "Morena Baccarin": "https://image.tmdb.org/t/p/w500/4YSd0s98duXWAYlZVnfUKwzh3Ij.jpg",
            
            # Joker: Folie à Deux
            "Joaquin Phoenix": "https://image.tmdb.org/t/p/w500/nXMzvVF6xR3OXOedozfLEbtc6Op.jpg",
            "Lady Gaga": "https://image.tmdb.org/t/p/w500/6COmYeLsz4cLsET0vlOSNvWpBnE.jpg",
            "Brendan Gleeson": "https://image.tmdb.org/t/p/w500/2v9FVVBUrrkW2m3QOcYkuhq9A6o.jpg",
            "Catherine Keener": "https://image.tmdb.org/t/p/w500/5wPOX8VlPCzaM8wjZFGbnKZjLpx.jpg",
            
            # Wicked
            "Cynthia Erivo": "https://image.tmdb.org/t/p/w500/9NSc5ykfBoaBcJlZ09QFp7b6r4A.jpg",
            "Ariana Grande": "https://image.tmdb.org/t/p/w500/9x7o2QJv2wJWQJ3oWQ5X3Q5Q5Q5.jpg",
            "Michelle Yeoh": "https://image.tmdb.org/t/p/w500/9NSc5ykfBoaBcJlZ09QFp7b6r4A.jpg",
            "Jeff Goldblum": "https://image.tmdb.org/t/p/w500/z2FA8js799xqtfiFjBTicFYdfk.jpg",
            
            # Gladiator II
            "Denzel Washington": "https://image.tmdb.org/t/p/w500/9x7o2QJv2wJWQJ3oWQ5X3Q5Q5Q5.jpg",
            "Pedro Pascal": "https://image.tmdb.org/t/p/w500/5XBzD5WuTyVQZeS4VI25z2moMeY.jpg",
            "Lior Raz": "https://image.tmdb.org/t/p/w500/4u5RJy7C8U6B0RdxTgJsWW6HlSR.jpg",
            "May Calamawy": "https://image.tmdb.org/t/p/w500/4YSd0s98duXWAYlZVnfUKwzh3Ij.jpg",
            
            # Avengers: Doomsday
            "Robert Downey Jr.": "https://image.tmdb.org/t/p/w500/5qHNjhtjMD4YWH3UP0rm4tKwxCL.jpg",
            "Chris Evans": "https://image.tmdb.org/t/p/w500/3bOGNsHlrswhyW79uvIHH1V43JI.jpg",
            "Chris Hemsworth": "https://image.tmdb.org/t/p/w500/2v9FVVBUrrkW2m3QOcYkuhq9A6o.jpg",
            "Scarlett Johansson": "https://image.tmdb.org/t/p/w500/6NsMbJXRlDZuDzatN2akFdGuTvx.jpg",
            
            # Star Wars: Episode X
            "Daisy Ridley": "https://image.tmdb.org/t/p/w500/9NSc5ykfBoaBcJlZ09QFp7b6r4A.jpg",
            "Adam Driver": "https://image.tmdb.org/t/p/w500/5XBzD5WuTyVQZeS4VI25z2moMeY.jpg",
            "John Boyega": "https://image.tmdb.org/t/p/w500/9x7o2QJv2wJWQJ3oWQ5X3Q5Q5Q5.jpg",
            "Oscar Isaac": "https://image.tmdb.org/t/p/w500/2v9FVVBUrrkW2m3QOcYkuhq9A6o.jpg",
            
            # New SHOWING movies cast
            # Fast X
            "Vin Diesel": "https://image.tmdb.org/t/p/w500/nZdVry7lnQOpDRJg9hPd0l10rNf.jpg",
            "Michelle Rodriguez": "https://image.tmdb.org/t/p/w500/xSvJAtGCbOCOCH5xOgDPYV2wBHb.jpg",
            "Tyrese Gibson": "https://image.tmdb.org/t/p/w500/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
            "Ludacris": "https://image.tmdb.org/t/p/w500/alakSDJGAhJdCGBNtGKqPCMnfDA.jpg",
            
            # Indiana Jones and the Dial of Destiny
            "Harrison Ford": "https://image.tmdb.org/t/p/w500/7CcoVFTogx0dWLPebNTcBKXdAUT.jpg",
            "Phoebe Waller-Bridge": "https://image.tmdb.org/t/p/w500/9NSc5ykfBoaBcJlZ09QFp7b6r4A.jpg",
            "Antonio Banderas": "https://image.tmdb.org/t/p/w500/yFuTYcnzPCCGDzSJJqp9wVV4rX4.jpg",
            "Shaunette Renée Wilson": "https://image.tmdb.org/t/p/w500/4YSd0s98duXWAYlZVnfUKwzh3Ij.jpg",
            
            # The Flash
            "Ezra Miller": "https://image.tmdb.org/t/p/w500/s6sTDJNzdOezX9s7sZYIgNbAG3p.jpg",
            "Sasha Calle": "https://image.tmdb.org/t/p/w500/9NSc5ykfBoaBcJlZ09QFp7b6r4A.jpg",
            "Michael Shannon": "https://image.tmdb.org/t/p/w500/2v9FVVBUrrkW2m3QOcYkuhq9A6o.jpg",
            "Ron Livingston": "https://image.tmdb.org/t/p/w500/5wPOX8VlPCzaM8wjZFGbnKZjLpx.jpg",
            
            # Transformers: Rise of the Beasts
            "Anthony Ramos": "https://image.tmdb.org/t/p/w500/lDHzYVWRAgJc2UIYO7X9wuYSCBd.jpg",
            "Dominique Fishback": "https://image.tmdb.org/t/p/w500/4YSd0s98duXWAYlZVnfUKwzh3Ij.jpg",
            "Luna Lauren Velez": "https://image.tmdb.org/t/p/w500/4YSd0s98duXWAYlZVnfUKwzh3Ij.jpg",
            "Dean Scott Vazquez": "https://image.tmdb.org/t/p/w500/5wPOX8VlPCzaM8wjZFGbnKZjLpx.jpg",
            
            # Wonka
            "Timothée Chalamet": "https://image.tmdb.org/t/p/w500/BE2sdjpgsa2rNTFa66f7upDjmjr.jpg",
            "Calah Lane": "https://image.tmdb.org/t/p/w500/4YSd0s98duXWAYlZVnfUKwzh3Ij.jpg",
            "Keegan-Michael Key": "https://image.tmdb.org/t/p/w500/vbttakOzP1bEHfGHjqZH4nveJTk.jpg",
            "Paterson Joseph": "https://image.tmdb.org/t/p/w500/5wPOX8VlPCzaM8wjZFGbnKZjLpx.jpg",
            
            # Aquaman and the Lost Kingdom
            "Jason Momoa": "https://image.tmdb.org/t/p/w500/PSK6GmsVwdhqz9cd1lwzC6a7EA.jpg",
            "Patrick Wilson": "https://image.tmdb.org/t/p/w500/tc5h5lFTlTdHOZnKlVGbQm4KkmA.jpg",
            "Yahya Abdul-Mateen II": "https://image.tmdb.org/t/p/w500/2FF3Yjxd7DYR6r8A9jgWEUm2RVu.jpg",
            "Amber Heard": "https://image.tmdb.org/t/p/w500/p4EHNhIePaIq7Yf45ZTYMFKbdEL.jpg",
            
            # The Marvels
            "Brie Larson": "https://image.tmdb.org/t/p/w500/iqaHjbhKOGEJJMjk2PbA1vuLMJW.jpg",
            "Teyonah Parris": "https://image.tmdb.org/t/p/w500/4YSd0s98duXWAYlZVnfUKwzh3Ij.jpg",
            "Iman Vellani": "https://image.tmdb.org/t/p/w500/9NSc5ykfBoaBcJlZ09QFp7b6r4A.jpg",
            
            # Anyone But You
            "Sydney Sweeney": "https://image.tmdb.org/t/p/w500/qYiaSl0Eb7G3VaxOg8PxExCFwon.jpg",
            "Glen Powell": "https://image.tmdb.org/t/p/w500/zM5nSYoMZbhFe3MaozWuPcTjWHO.jpg",
            "Alexandra Shipp": "https://image.tmdb.org/t/p/w500/4YSd0s98duXWAYlZVnfUKwzh3Ij.jpg",
            "Hadley Robinson": "https://image.tmdb.org/t/p/w500/9NSc5ykfBoaBcJlZ09QFp7b6r4A.jpg"
        }
        
        movies = []
        today = date.today()
        
        for movie_data in movies_data:
            # Assign movie state based on release date
            release_date = movie_data.get("release_date", today)
            if release_date > today:
                movie_data["state"] = MovieState.COMING_SOON
            elif release_date > (today - timedelta(days=90)):  # Movies released within 90 days are still showing
                movie_data["state"] = MovieState.SHOWING
            else:
                movie_data["state"] = MovieState.ENDED
                
            movie = Movie(**movie_data)
            session.add(movie)
            session.commit()
            session.refresh(movie)
            movies.append(movie)
            
            # Create cast entries with image URLs
            for idx, actor_name in enumerate(movie_data["cast"][:4]):  # Top 4 actors
                cast_entry = Cast(
                    movie_id=movie.id,
                    actor_name=actor_name,
                    character_name=f"Character {idx + 1}",  # Placeholder
                    role="Actor",
                    profile_image_url=cast_details.get(actor_name),
                    is_lead=(idx < 2),  # First 2 are leads
                    order=idx
                )
                session.add(cast_entry)
            
            print(f"   ✓ Created movie: {movie.title} with cast")
        
        session.commit()
        print(f"   ✓ Created {len(movies)} movies with cast details")
        
        # Create screenings (yesterday to next 8 days) - only for SHOWING movies
        print("\n📅 Creating screenings...")
        base_date = datetime.now() - timedelta(days=1)  # Yesterday
        screening_count = 0
        
        # Filter movies to only include SHOWING movies (no screenings for COMING_SOON or ENDED)
        showing_movies = [movie for movie in movies if movie.state == MovieState.SHOWING]
        coming_soon_count = len([movie for movie in movies if movie.state == MovieState.COMING_SOON])
        ended_count = len([movie for movie in movies if movie.state == MovieState.ENDED])
        
        print(f"Found {len(showing_movies)} SHOWING movies")
        print(f"Skipping {coming_soon_count} COMING_SOON movies and {ended_count} ENDED movies")
        
        for day in range(9):  # 9 days total (yesterday to 8 days ahead)
            current_date = base_date + timedelta(days=day)
            
            # Morning, afternoon, evening, night showtimes
            times = [10, 14, 18, 21]
            
            for idx, movie in enumerate(showing_movies):  # Only SHOWING movies
                # Rotate through rooms
                room = rooms[idx % len(rooms)]
                
                for time_hour in times:
                    screening_time = current_date.replace(hour=time_hour, minute=0, second=0)
                    
                    # Check if screening already exists
                    existing = session.exec(
                        select(Screening).where(
                            Screening.movie_id == movie.id,
                            Screening.room_id == room.id,
                            Screening.screening_time == screening_time
                        )
                    ).first()
                    
                    if existing:
                        continue
                    
                    # IMAX/VIP rooms cost more
                    base_price = 25.0 if "IMAX" in room.name or "VIP" in room.name else 15.0
                    # Evening/night shows cost more
                    price = base_price + 5.0 if time_hour >= 18 else base_price
                    
                    screening = Screening(
                        movie_id=movie.id,
                        room_id=room.id,
                        screening_time=screening_time,
                        price=price
                    )
                    session.add(screening)
                    screening_count += 1
        
        if screening_count > 0:
            session.commit()
        print(f"   ✓ Created {screening_count} new screenings")
        
        print("\n✅ Database seeding completed successfully!")
        print(f"\n📊 Summary:")
        print(f"   - {len(cinemas)} cinemas")
        print(f"   - {len(rooms)} rooms")
        print(f"   - {total_seats} seats (7 rows x 10 seats per room)")
        print(f"   - {len(movies)} movies with cast details and image URLs")
        print(f"   - {screening_count} screenings")
        print(f"   - 1 demo user (email: demo@cinema.com, password: demo123)")
        print(f"   - 1 admin user (email: admin@cinema.com, password: admin123)")


def add_screenings_for_movie(session: Session, movie_id: int):
    """Add screenings for a specific movie across all cinemas."""
    print(f"🎬 Adding screenings for movie ID {movie_id} across all cinemas...")

    # Get all cinemas
    cinemas = session.exec(select(Cinema)).all()
    print(f"Found {len(cinemas)} cinemas")

    # Get all rooms
    rooms = session.exec(select(Room)).all()
    print(f"Found {len(rooms)} rooms")

    screenings_added = 0

    # For each cinema, add screenings in their rooms
    for cinema in cinemas:
        cinema_rooms = [room for room in rooms if room.cinema_id == cinema.id]
        print(f"\n🎭 Processing {cinema.name} ({len(cinema_rooms)} rooms)")

        # Add screenings for next 3 days
        for day_offset in range(1, 4):  # Tomorrow, day after, etc.
            screening_date = datetime.now() + timedelta(days=day_offset)

            # Different showtimes for each day
            showtimes = [
                (10, 0),  # 10:00 AM
                (14, 30), # 2:30 PM
                (18, 0),  # 6:00 PM
                (21, 0),  # 9:00 PM
            ]

            for hour, minute in showtimes:
                screening_time = screening_date.replace(hour=hour, minute=minute, second=0, microsecond=0)

                # Add screening in each room of this cinema
                for room in cinema_rooms:
                    # Check if screening already exists
                    existing = session.exec(
                        select(Screening).where(
                            Screening.movie_id == movie_id,
                            Screening.room_id == room.id,
                            Screening.screening_time == screening_time
                        )
                    ).first()

                    if existing:
                        print(f"   ⏭️  Screening already exists: {cinema.name} - {room.name} at {screening_time}")
                        continue

                    # Determine price based on room type
                    base_price = 25.0 if "IMAX" in room.name or "VIP" in room.name else 15.0
                    # Evening/night shows cost more
                    price = base_price + 5.0 if hour >= 18 else base_price

                    screening = Screening(
                        movie_id=movie_id,
                        room_id=room.id,
                        screening_time=screening_time,
                        price=price
                    )
                    session.add(screening)
                    screenings_added += 1
                    print(f"   ✅ Added screening: {cinema.name} - {room.name} at {screening_time.strftime('%Y-%m-%d %H:%M')} (${price})")

    if screenings_added > 0:
        session.commit()
        print(f"\n🎉 Successfully added {screenings_added} new screenings for movie ID {movie_id}!")
    else:
        print(f"\nℹ️  No new screenings were added for movie ID {movie_id} (all already exist)")


if __name__ == "__main__":
    seed_database()
