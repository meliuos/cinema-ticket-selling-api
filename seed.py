"""
Database seeding script.

Run this to populate the database with sample data for development/testing.
"""
from datetime import datetime, timedelta, date
from sqlmodel import Session, create_engine, select

from app.config import settings
from app.database import engine
from app.models import Cinema, Room, Seat, Movie, Screening, User, Cast, Ticket, Review, Favorite, SearchHistory, TokenBlacklist
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
        }
        
        movies = []
        for movie_data in movies_data:
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
        
        # Create screenings (yesterday to next 8 days)
        print("\n📅 Creating screenings...")
        base_date = datetime.now() - timedelta(days=1)  # Yesterday
        screening_count = 0
        
        for day in range(9):  # 9 days total (yesterday to 8 days ahead)
            current_date = base_date + timedelta(days=day)
            
            # Morning, afternoon, evening, night showtimes
            times = [10, 14, 18, 21]
            
            for idx, movie in enumerate(movies):  # All movies
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
    
    # Add additional screenings for specific movies
    with Session(engine) as session:
        add_screenings_for_movie(session, 8)  # Add screenings for movie ID 8
