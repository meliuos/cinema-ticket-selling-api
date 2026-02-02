"""
Database seeding script.

Run this to populate the database with sample data for development/testing.
"""
from datetime import datetime, timedelta, date
from sqlmodel import Session, create_engine, select, text

from app.config import settings
from app.database import engine
from app.models import Cinema, Room, Seat, Movie, Screening, User, Cast, MovieState, Review, FAQ
from app.services.auth import get_password_hash
from sqlmodel import SQLModel



def clear_database(session: Session):
    """Clear all data from the database to avoid duplicates."""
    print("🗑️  Clearing existing data...")
    
    from sqlalchemy import text
    
    # Truncate all tables with CASCADE to handle dependencies
    session.execute(text('TRUNCATE TABLE "user", movie, cinema, room, seat, screening, "cast", ticket, reviews, review_reactions, favorite, search_history, tokenblacklist, faq CASCADE;'))
    
    session.commit()
    print("   ✓ All existing data cleared")


def seed_database():
    """Seed the database with sample data."""
    print("🌱 Starting database seeding...")
    
    with Session(engine) as session:
        clear_database(session)
        
        # Create sample users (for testing ticket booking)
        print("👤 Creating sample users...")
        users = []
        
        # Create demo user
        demo_user = User(
            email="demo@cinema.com",
            full_name="Demo User",
            hashed_password=get_password_hash("demo123"),
            is_active=True
        )
        session.add(demo_user)
        users.append(demo_user)
        
        # Create admin user
        admin_user = User(
            email="admin@cinema.com",
            full_name="Admin User",
            hashed_password=get_password_hash("admin123"),
            is_active=True,
            is_admin=True
        )
        session.add(admin_user)
        users.append(admin_user)
        
        # Create superuser admin
        superuser_admin = User(
            email="superuser@cinema.com",
            full_name="Superuser Admin",
            hashed_password=get_password_hash("super123"),
            is_active=True,
            is_admin=True
        )
        session.add(superuser_admin)
        users.append(superuser_admin)
        
        # Create the admin
        the_admin = User(
            email="the.admin@cinema.com",
            full_name="The Admin",
            hashed_password=get_password_hash("admin"),
            is_active=True,
            is_admin=True
        )
        session.add(the_admin)
        users.append(the_admin)
        
        # Create additional users
        additional_users = [
            ("user1@cinema.com", "John Smith", "user123"),
            ("user2@cinema.com", "Sarah Johnson", "user123"),
            ("user3@cinema.com", "Mike Davis", "user123"),
            ("user4@cinema.com", "Emma Wilson", "user123"),
            ("user5@cinema.com", "David Brown", "user123"),
            ("user6@cinema.com", "Lisa Garcia", "user123"),
            ("user7@cinema.com", "Tom Miller", "user123"),
            ("user8@cinema.com", "Anna Martinez", "user123"),
            ("user9@cinema.com", "Chris Anderson", "user123"),
            ("user10@cinema.com", "Rachel Taylor", "user123"),
            ("user11@cinema.com", "Kevin Thomas", "user123"),
            ("user12@cinema.com", "Michelle Lee", "user123"),
            ("user13@cinema.com", "Jason White", "user123"),
            ("user14@cinema.com", "Amanda Harris", "user123"),
            ("user15@cinema.com", "Ryan Clark", "user123"),
            ("user16@cinema.com", "Nicole Lewis", "user123"),
            ("user17@cinema.com", "Tyler Robinson", "user123"),
            ("user18@cinema.com", "Olivia Walker", "user123")
        ]
        
        for email, name, password in additional_users:
            user = User(
                email=email,
                full_name=name,
                hashed_password=get_password_hash(password),
                is_active=True
            )
            session.add(user)
            users.append(user)
        
        session.commit()
        for user in users:
            session.refresh(user)
        print(f"   ✓ Created {len(users)} users ({len([u for u in users if u.is_admin])} admin, {len([u for u in users if not u.is_admin])} regular)")
        
        # Create cinemas
        print("\n🎬 Creating cinemas...")
        cinemas = [
            Cinema(name="Mega Cinema Tunis", address="123 Avenue Habib Bourguiba", city="Tunis",
                   amenities=["IMAX", "3D", "4DX", "Dolby Atmos", "VIP Seats", "Recliner Seats", "Multiple Screens", "Wheelchair Accessible", "Food Court", "Online Booking", "Parking", "Air Conditioning", "VIP Lounge"]),
            Cinema(name="Pathé Palace", address="456 Avenue de la Liberté", city="Tunis",
                   amenities=["3D", "Dolby Surround", "Premium Seats", "Comfortable Seats", "Multiple Screens", "Wheelchair Accessible", "Hearing Assistance", "Snack Bar", "Cafe", "Online Tickets", "Parking", "Air Conditioning"]),
            Cinema(name="CinéMadart", address="789 Rue de Marseille", city="Tunis",
                   amenities=["Digital Projection", "Standard Seats", "Wheelchair Accessible", "Concession Stand", "Online Booking", "Air Conditioning"]),
            Cinema(name="Le Colisée", address="321 Boulevard de la République", city="Sfax",
                   amenities=["3D", "Dolby Atmos", "Laser Projection", "VIP Seats", "Recliner Seats", "Multiple Screens", "Wheelchair Accessible", "Restaurant", "Alcohol Served", "Online Booking", "Parking", "Premium Sound"]),
            Cinema(name="Ciné Jamil", address="654 Avenue Farhat Hached", city="Sousse",
                   amenities=["3D", "Dolby Surround", "Premium Seats", "Multiple Screens", "Wheelchair Accessible", "Food Court", "Cafe", "Online Tickets", "Parking", "Air Conditioning"]),
            Cinema(name="Rialto Cinema", address="987 Rue de la Kasbah", city="Tunis",
                   amenities=["Digital Projection", "Comfortable Seats", "Standard Seats", "Snack Bar", "Online Booking", "Air Conditioning"]),
            Cinema(name="Ciné Atlas", address="147 Boulevard 9 Avril", city="Tunis",
                   amenities=["3D", "4DX", "Dolby Atmos", "Premium Seats", "Recliner Seats", "Multiple Screens", "Wheelchair Accessible", "Hearing Assistance", "Food Court", "Online Booking", "Online Tickets", "Parking", "Air Conditioning", "Premium Sound"]),
            Cinema(name="Le Palace", address="258 Rue de Rome", city="Monastir",
                   amenities=["3D", "Dolby Surround", "VIP Seats", "Premium Seats", "Multiple Screens", "Wheelchair Accessible", "Restaurant", "Cafe", "Alcohol Served", "Online Booking", "Parking", "Air Conditioning", "VIP Lounge"]),
            Cinema(name="Ciné Rex", address="369 Avenue de France", city="Bizerte",
                   amenities=["Digital Projection", "Standard Seats", "Comfortable Seats", "Concession Stand", "Snack Bar", "Online Tickets", "Air Conditioning"]),
            Cinema(name="Majestic Cinema", address="741 Rue de l'Indépendance", city="Gabès",
                   amenities=["3D", "Laser Projection", "Premium Seats", "Multiple Screens", "Wheelchair Accessible", "Food Court", "Online Booking", "Parking", "Air Conditioning"]),
            Cinema(name="Ciné Alhambra", address="852 Boulevard de l'Environnement", city="Ariana",
                   amenities=["IMAX", "3D", "Dolby Atmos", "VIP Seats", "Recliner Seats", "Multiple Screens", "Wheelchair Accessible", "Hearing Assistance", "Restaurant", "Cafe", "Online Booking", "Online Tickets", "Parking", "Air Conditioning", "Premium Sound"]),
            Cinema(name="Le Royal", address="963 Avenue de la Victoire", city="Kairouan",
                   amenities=["Digital Projection", "Comfortable Seats", "Standard Seats", "Snack Bar", "Online Booking", "Air Conditioning"]),
            Cinema(name="Ciné Étoile", address="159 Rue de la Révolution", city="Nabeul",
                   amenities=["3D", "Dolby Surround", "Premium Seats", "Multiple Screens", "Wheelchair Accessible", "Food Court", "Online Tickets", "Parking", "Air Conditioning"]),
            Cinema(name="Palais du Cinéma", address="357 Boulevard de la Paix", city="Hammamet",
                   amenities=["3D", "4DX", "Dolby Atmos", "VIP Seats", "Recliner Seats", "Multiple Screens", "Wheelchair Accessible", "Restaurant", "Alcohol Served", "Online Booking", "Parking", "Air Conditioning", "VIP Lounge"]),
            Cinema(name="Ciné Moderne", address="468 Avenue de la Liberté", city="Mahdia",
                   amenities=["Digital Projection", "Laser Projection", "Comfortable Seats", "Wheelchair Accessible", "Snack Bar", "Cafe", "Online Booking", "Air Conditioning"]),
            Cinema(name="Ciné Luxor", address="512 Avenue Bourguiba", city="La Marsa",
                   amenities=["IMAX", "3D", "Dolby Atmos", "Laser Projection", "VIP Seats", "Premium Seats", "Recliner Seats", "Multiple Screens", "Wheelchair Accessible", "Hearing Assistance", "Food Court", "Restaurant", "Alcohol Served", "Online Booking", "Online Tickets", "Parking", "Air Conditioning", "Premium Sound", "VIP Lounge"]),
            Cinema(name="Star Cinema", address="678 Rue de Carthage", city="Carthage",
                   amenities=["3D", "Dolby Surround", "Premium Seats", "Multiple Screens", "Wheelchair Accessible", "Food Court", "Cafe", "Online Booking", "Parking", "Air Conditioning"]),
            Cinema(name="Le Grand Rex", address="890 Boulevard de la Corniche", city="Sousse",
                   amenities=["IMAX", "3D", "4DX", "Dolby Atmos", "VIP Seats", "Recliner Seats", "Multiple Screens", "Wheelchair Accessible", "Restaurant", "Online Booking", "Online Tickets", "Parking", "Air Conditioning", "Premium Sound", "VIP Lounge"]),
            Cinema(name="Ciné Carthage", address="234 Avenue Habib Thameur", city="Tunis",
                   amenities=["3D", "Laser Projection", "Dolby Surround", "Premium Seats", "Comfortable Seats", "Multiple Screens", "Wheelchair Accessible", "Snack Bar", "Cafe", "Online Tickets", "Parking", "Air Conditioning"]),
            Cinema(name="Empire Cinema", address="567 Rue Charles de Gaulle", city="Sfax",
                   amenities=["3D", "4DX", "Dolby Atmos", "VIP Seats", "Premium Seats", "Recliner Seats", "Multiple Screens", "Wheelchair Accessible", "Food Court", "Restaurant", "Online Booking", "Parking", "Air Conditioning", "Premium Sound"])
        ]
        
        for cinema in cinemas:
            session.add(cinema)
        session.commit()
        print(f"   ✓ Created {len(cinemas)} cinemas")
        
        # Create rooms for all cinemas
        print("\n🚪 Creating rooms...")
        rooms = []
        
        for cinema in cinemas:
            # Each cinema gets 2-3 rooms
            num_rooms = 3 if cinema.id % 3 == 0 else 2  # Some cinemas have 3 rooms
            
            for i in range(num_rooms):
                room_name = f"Room {i+1}" if i < 2 else "IMAX"
                room = Room(name=room_name, cinema_id=cinema.id)
                session.add(room)
                rooms.append(room)
        
        session.commit()
        
        # Refresh all rooms
        for room in rooms:
            session.refresh(room)
        
        # Create seats for each room - 7 rows x 10 seats
        print("\n💺 Creating seats (7 rows x 10 seats each)...")
        total_seats = 0
        
        for room in rooms:
            # Standard rooms: 8 rows x 12 seats, IMAX: 12 rows x 20 seats
            rows = 12 if room.name == "IMAX" else 8
            seats_per_row = 20 if room.name == "IMAX" else 12
            
            for row_num in range(rows):
                row_label = chr(65 + row_num) if row_num < 26 else f"A{chr(65 + row_num - 26)}"

                for seat_num in range(1, seats_per_row + 1):
                    seat_type = "vip" if row_num >= rows - 2 else "standard"
                    seat = Seat(
                        room_id=room.id,
                        row_label=row_label,
                        seat_number=seat_num,
                        seat_type="standard"
                    )
                    session.add(seat)
                    total_seats += 1
            
            print(f"   ✓ Created {rows * seats_per_row} seats for {room.name}")
        
        session.commit()
        print(f"   Total seats created: {total_seats}")
        
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
            ),
            Movie(
                title="The Shawshank Redemption",
                description="Two imprisoned men bond over a number of years, finding solace and eventual redemption through acts of common decency.",
                duration_minutes=142,
                genre="Drama",
                rating="R",
                cast=["Tim Robbins", "Morgan Freeman", "Bob Gunton", "William Sadler"],
                director="Frank Darabont",
                writers=["Frank Darabont"],
                producers=["Niki Marvin"],
                release_date=date(1994, 9, 23),
                country="USA",
                language="English",
                budget=25000000,
                revenue=28341469,
                production_company="Castle Rock Entertainment",
                distributor="Columbia Pictures",
                image_url="https://image.tmdb.org/t/p/w500/q6y0Go1tsGEsmtFryDOJo3dEmqu.jpg",
                trailer_url="https://www.youtube.com/watch?v=6hB3S9bIaco",
                awards=["Multiple awards including AFI's 100 Years...100 Movies"],
                details={"imdb_rating": 9.3, "based_on": "Stephen King novella"}
            ),
            Movie(
                title="Forrest Gump",
                description="The presidencies of Kennedy and Johnson, Vietnam, Watergate, and other history unfold through the perspective of an Alabama man with an IQ of 75.",
                duration_minutes=142,
                genre="Drama",
                rating="PG-13",
                cast=["Tom Hanks", "Robin Wright", "Gary Sinise", "Sally Field"],
                director="Robert Zemeckis",
                writers=["Winston Groom", "Eric Roth"],
                producers=["Wendy Finerman", "Steve Tisch"],
                release_date=date(1994, 7, 6),
                country="USA",
                language="English",
                budget=55000000,
                revenue=677387716,
                production_company="Paramount Pictures",
                distributor="Paramount Pictures",
                image_url="https://image.tmdb.org/t/p/w500/arw2vcBveWOVZr6pxd9XTd1TdQa.jpg",
                trailer_url="https://www.youtube.com/watch?v=bLvqoHBptjg",
                awards=["Academy Award for Best Picture", "Academy Award for Best Director"],
                details={"imdb_rating": 8.8, "cultural_impact": "High"}
            ),
            Movie(
                title="The Godfather",
                description="The aging patriarch of an organized crime dynasty transfers control of his clandestine empire to his reluctant son.",
                duration_minutes=175,
                genre="Crime",
                rating="R",
                cast=["Marlon Brando", "Al Pacino", "James Caan", "Richard S. Castellano"],
                director="Francis Ford Coppola",
                writers=["Mario Puzo", "Francis Ford Coppola"],
                producers=["Albert S. Ruddy"],
                release_date=date(1972, 3, 24),
                country="USA",
                language="English",
                budget=6000000,
                revenue=134966411,
                production_company="Paramount Pictures",
                distributor="Paramount Pictures",
                image_url="https://image.tmdb.org/t/p/w500/3bhkrj58Vtu7enYsRolD1fZdja1.jpg",
                trailer_url="https://www.youtube.com/watch?v=sY1S34973zI",
                awards=["Academy Award for Best Picture", "Academy Award for Best Actor"],
                details={"imdb_rating": 9.2, "trilogy": "The Godfather Trilogy", "part": 1}
            ),
            Movie(
                title="The Lord of the Rings: The Fellowship of the Ring",
                description="A meek Hobbit from the Shire and eight companions set out on a journey to destroy the powerful One Ring.",
                duration_minutes=178,
                genre="Fantasy",
                rating="PG-13",
                cast=["Elijah Wood", "Ian McKellen", "Orlando Bloom", "Sean Bean"],
                director="Peter Jackson",
                writers=["J.R.R. Tolkien", "Fran Walsh", "Philippa Boyens"],
                producers=["Peter Jackson", "Fran Walsh"],
                release_date=date(2001, 12, 19),
                country="New Zealand",
                language="English",
                budget=93000000,
                revenue=871368364,
                production_company="New Line Cinema",
                distributor="New Line Cinema",
                image_url="https://image.tmdb.org/t/p/w500/6oom5QYQ2yQTMJIbnvbkBL9cHo6.jpg",
                trailer_url="https://www.youtube.com/watch?v=V75dMMIW2B4",
                awards=["Academy Award for Best Cinematography", "Academy Award for Best Original Score"],
                details={"trilogy": "The Lord of the Rings Trilogy", "part": 1, "imdb_rating": 8.8}
            ),
            Movie(
                title="Fight Club",
                description="An insomniac office worker and a devil-may-care soapmaker form an underground fight club.",
                duration_minutes=139,
                genre="Drama",
                rating="R",
                cast=["Brad Pitt", "Edward Norton", "Helena Bonham Carter", "Meat Loaf"],
                director="David Fincher",
                writers=["Chuck Palahniuk", "Jim Uhls"],
                producers=["Art Linson", "Ceán Chaffin"],
                release_date=date(1999, 10, 15),
                country="USA",
                language="English",
                budget=63000000,
                revenue=100853753,
                production_company="20th Century Fox",
                distributor="20th Century Fox",
                image_url="https://image.tmdb.org/t/p/w500/pB8BM7pdSp6B6Ih7QZ4DrQ3PmJK.jpg",
                trailer_url="https://www.youtube.com/watch?v=SUXWAEX2jlg",
                awards=["No major awards but cult classic"],
                details={"imdb_rating": 8.8, "based_on": "Chuck Palahniuk novel"}
            ),
            Movie(
                title="The Avengers",
                description="Earth's mightiest heroes must come together and learn to fight as a team to stop the mischievous Loki.",
                duration_minutes=143,
                genre="Action",
                rating="PG-13",
                cast=["Robert Downey Jr.", "Chris Evans", "Scarlett Johansson", "Jeremy Renner"],
                director="Joss Whedon",
                writers=["Joss Whedon"],
                producers=["Kevin Feige"],
                release_date=date(2012, 5, 4),
                country="USA",
                language="English",
                budget=220000000,
                revenue=1518812988,
                production_company="Marvel Studios",
                distributor="Walt Disney Studios Motion Pictures",
                image_url="https://image.tmdb.org/t/p/w500/RYMX2wcKCBAr24UyPD7xwmjaTn.jpg",
                trailer_url="https://www.youtube.com/watch?v=eOrNdBpGMv8",
                awards=["No Academy Awards but box office success"],
                details={"franchise": "Marvel Cinematic Universe", "imdb_rating": 8.0}
            ),
            Movie(
                title="Gladiator",
                description="A former Roman General sets out to exact vengeance against the corrupt emperor who murdered his family.",
                duration_minutes=155,
                genre="Action",
                rating="R",
                cast=["Russell Crowe", "Joaquin Phoenix", "Connie Nielsen", "Oliver Reed"],
                director="Ridley Scott",
                writers=["David Franzoni", "John Logan", "William Nicholson"],
                producers=["Douglas Wick", "David Franzoni"],
                release_date=date(2000, 5, 5),
                country="USA",
                language="English",
                budget=103000000,
                revenue=460583960,
                production_company="DreamWorks Pictures",
                distributor="DreamWorks Pictures",
                image_url="https://image.tmdb.org/t/p/w500/ty8TGRuvJLPUmAR1H1nRIsgwvim.jpg",
                trailer_url="https://www.youtube.com/watch?v=owK1qxDselE",
                awards=["Academy Award for Best Picture", "Academy Award for Best Actor"],
                details={"imdb_rating": 8.5, "historical_drama": True}
            ),
            Movie(
                title="Titanic",
                description="A seventeen-year-old aristocrat falls in love with a kind but poor artist aboard the luxurious, ill-fated R.M.S. Titanic.",
                duration_minutes=194,
                genre="Romance",
                rating="PG-13",
                cast=["Leonardo DiCaprio", "Kate Winslet", "Billy Zane", "Kathy Bates"],
                director="James Cameron",
                writers=["James Cameron"],
                producers=["James Cameron", "Jon Landau"],
                release_date=date(1997, 12, 19),
                country="USA",
                language="English",
                budget=200000000,
                revenue=2187463944,
                production_company="20th Century Fox",
                distributor="20th Century Fox",
                image_url="https://image.tmdb.org/t/p/w500/9xjZS2rlVxm8SFx8kPC3aIGCOYQ.jpg",
                trailer_url="https://www.youtube.com/watch?v=kVrqfYjkTdQ",
                awards=["Academy Award for Best Picture", "Academy Award for Best Director"],
                details={"imdb_rating": 7.9, "based_on": "Historical event"}
            ),
            Movie(
                title="The Silence of the Lambs",
                description="A young F.B.I. cadet must receive the help of an incarcerated and manipulative cannibal killer to help catch another serial killer.",
                duration_minutes=118,
                genre="Thriller",
                rating="R",
                cast=["Jodie Foster", "Anthony Hopkins", "Lawrence A. Bonney", "Kasi Lemmons"],
                director="Jonathan Demme",
                writers=["Thomas Harris", "Ted Tally"],
                producers=["Edward Saxon", "Kenneth Utt"],
                release_date=date(1991, 2, 14),
                country="USA",
                language="English",
                budget=19000000,
                revenue=272742922,
                production_company="Orion Pictures",
                distributor="Orion Pictures",
                image_url="https://image.tmdb.org/t/p/w500/uS9m8OBk1A8eM9I042bx8XXpqAq.jpg",
                trailer_url="https://www.youtube.com/watch?v=W6Mm8Sbe__o",
                awards=["Academy Award for Best Picture", "Academy Award for Best Actor"],
                details={"imdb_rating": 8.6, "based_on": "Thomas Harris novel"}
            ),
            Movie(
                title="Schindler's List",
                description="In German-occupied Poland during World War II, Oskar Schindler gradually becomes concerned for his Jewish workforce.",
                duration_minutes=195,
                genre="Historical",
                rating="R",
                cast=["Liam Neeson", "Ralph Fiennes", "Ben Kingsley", "Caroline Goodall"],
                director="Steven Spielberg",
                writers=["Steven Zaillian"],
                producers=["Steven Spielberg", "Gerald R. Molen"],
                release_date=date(1993, 12, 15),
                country="USA",
                language="English",
                budget=22000000,
                revenue=321365567,
                production_company="Universal Pictures",
                distributor="Universal Pictures",
                image_url="https://image.tmdb.org/t/p/w500/c8Ass7acuOe4za6DhSattE359gr.jpg",
                trailer_url="https://www.youtube.com/watch?v=gG22XNhtnoY",
                awards=["Academy Award for Best Picture", "Academy Award for Best Director"],
                details={"imdb_rating": 8.9, "based_on": "True story"}
            ),
            Movie(
                title="Goodfellas",
                description="The story of Henry Hill and his life in the mob, covering his relationship with his wife Karen Hill and his mob partners.",
                duration_minutes=146,
                genre="Crime",
                rating="R",
                cast=["Robert De Niro", "Ray Liotta", "Joe Pesci", "Lorraine Bracco"],
                director="Martin Scorsese",
                writers=["Nicholas Pileggi", "Martin Scorsese"],
                producers=["Irwin Winkler"],
                release_date=date(1990, 9, 21),
                country="USA",
                language="English",
                budget=25000000,
                revenue=46836394,
                production_company="Warner Bros. Pictures",
                distributor="Warner Bros. Pictures",
                image_url="https://image.tmdb.org/t/p/w500/aKuFiU82s5ISJpGZp7YkIr3kCUd.jpg",
                trailer_url="https://www.youtube.com/watch?v=qo5jJpHtI1Y",
                awards=["Academy Award for Best Supporting Actor", "Golden Globe for Best Motion Picture"],
                details={"imdb_rating": 8.7, "based_on": "Nicholas Pileggi book"}
            ),
            Movie(
                title="Jurassic Park",
                description="A pragmatic paleontologist visiting an almost complete theme park is tasked with protecting a couple of kids.",
                duration_minutes=127,
                genre="Sci-Fi",
                rating="PG-13",
                cast=["Sam Neill", "Laura Dern", "Jeff Goldblum", "Richard Attenborough"],
                director="Steven Spielberg",
                writers=["Michael Crichton", "David Koepp"],
                producers=["Kathleen Kennedy", "Gerald R. Molen"],
                release_date=date(1993, 6, 11),
                country="USA",
                language="English",
                budget=63000000,
                revenue=1029153882,
                production_company="Universal Pictures",
                distributor="Universal Pictures",
                image_url="https://image.tmdb.org/t/p/w500/oU7Oq2kFAAlGqbU4VoAE36g4hoI.jpg",
                trailer_url="https://www.youtube.com/watch?v=lc0UehYemQA",
                awards=["Academy Award for Best Sound", "Academy Award for Best Visual Effects"],
                details={"imdb_rating": 8.1, "franchise": "Jurassic Park", "part": 1}
            ),
            Movie(
                title="Terminator 2: Judgment Day",
                description="A cyborg, identical to the one who failed to kill Sarah Connor, must now protect her teenage son, John Connor.",
                duration_minutes=137,
                genre="Action",
                rating="R",
                cast=["Arnold Schwarzenegger", "Linda Hamilton", "Edward Furlong", "Robert Patrick"],
                director="James Cameron",
                writers=["James Cameron", "William Wisher"],
                producers=["James Cameron"],
                release_date=date(1991, 7, 3),
                country="USA",
                language="English",
                budget=102000000,
                revenue=520000000,
                production_company="TriStar Pictures",
                distributor="TriStar Pictures",
                image_url="https://image.tmdb.org/t/p/w1280/5M0j0B18abtBI5gi2RhfjjurTqb.jpg",
                trailer_url="https://www.youtube.com/watch?v=lwSysg9o7wE",
                awards=["Academy Award for Best Sound", "Academy Award for Best Visual Effects"],
                details={"imdb_rating": 8.5, "franchise": "Terminator", "part": 2}
            ),
            Movie(
                title="The Usual Suspects",
                description="A sole survivor tells of the twisty events leading up to a horrific gun battle on a boat, which began when five criminals met at a seemingly random police lineup.",
                duration_minutes=106,
                genre="Crime",
                rating="R",
                cast=["Kevin Spacey", "Gabriel Byrne", "Benicio del Toro", "Kevin Pollak"],
                director="Bryan Singer",
                writers=["Christopher McQuarrie"],
                producers=["Michael McDonnell"],
                release_date=date(1995, 8, 16),
                country="USA",
                language="English",
                budget=6000000,
                revenue=23341568,
                production_company="PolyGram Filmed Entertainment",
                distributor="Gramercy Pictures",
                image_url="https://image.tmdb.org/t/p/w500/AuGiPiGMYMkSosOJ3BQjDEAiwtO.jpg",
                trailer_url="https://www.youtube.com/watch?v=Q0eCIYtJa8Q",
                awards=["Academy Award for Best Supporting Actor", "Academy Award for Best Original Screenplay"],
                details={"imdb_rating": 8.5, "twist_ending": True}
            ),
            Movie(
                title="Seven",
                description="Two detectives, a rookie and a veteran, hunt a serial killer who uses the seven deadly sins as his modus operandi.",
                duration_minutes=127,
                genre="Crime",
                rating="R",
                cast=["Brad Pitt", "Morgan Freeman", "Gwyneth Paltrow", "Kevin Spacey"],
                director="David Fincher",
                writers=["Andrew Kevin Walker"],
                producers=["Arnold Kopelson"],
                release_date=date(1995, 9, 22),
                country="USA",
                language="English",
                budget=33000000,
                revenue=327311859,
                production_company="New Line Cinema",
                distributor="New Line Cinema",
                image_url="https://image.tmdb.org/t/p/w500/69Sns8WoET6CfaYlIkHbla4l7nC.jpg",
                trailer_url="https://www.youtube.com/watch?v=znmZoVkCjpI",
                awards=["No major Academy Awards but critically acclaimed"],
                details={"imdb_rating": 8.6, "psychological_thriller": True}
            ),
            Movie(
                title="The Green Mile",
                description="The lives of guards on Death Row are affected by one of their charges: a black man accused of child murder and rape.",
                duration_minutes=189,
                genre="Drama",
                rating="R",
                cast=["Tom Hanks", "Michael Clarke Duncan", "David Morse", "Bonnie Hunt"],
                director="Frank Darabont",
                writers=["Frank Darabont"],
                producers=["Frank Darabont", "David Valdes"],
                release_date=date(1999, 12, 10),
                country="USA",
                language="English",
                budget=60000000,
                revenue=286801374,
                production_company="Castle Rock Entertainment",
                distributor="Warner Bros. Pictures",
                image_url="https://image.tmdb.org/t/p/w500/velWPhVMQeQKcxggNEU8YmIo52R.jpg",
                trailer_url="https://www.youtube.com/watch?v=Ki4haFrqSrw",
                awards=["Academy Award for Best Supporting Actor", "Golden Globe for Best Motion Picture"],
                details={"imdb_rating": 8.6, "based_on": "Stephen King novella"}
            ),
            Movie(
                title="American Beauty",
                description="A sexually frustrated suburban father has a mid-life crisis after becoming infatuated with his daughter's best friend.",
                duration_minutes=122,
                genre="Drama",
                rating="R",
                cast=["Kevin Spacey", "Annette Bening", "Thora Birch", "Wes Bentley"],
                director="Sam Mendes",
                writers=["Alan Ball"],
                producers=["Bruce Cohen", "Dan Jinks"],
                release_date=date(1999, 9, 15),
                country="USA",
                language="English",
                budget=15000000,
                revenue=356296601,
                production_company="DreamWorks Pictures",
                distributor="DreamWorks Pictures",
                image_url="https://image.tmdb.org/t/p/w500/wby9315QzVKdW9BonAefg8jGTTb.jpg",
                trailer_url="https://www.youtube.com/watch?v=3ycmmJ6rxA8",
                awards=["Academy Award for Best Picture", "Academy Award for Best Director"],
                details={"imdb_rating": 8.3, "satire": True}
            ),
            Movie(
                title="Saving Private Ryan",
                description="Following the Normandy Landings, a group of U.S. soldiers go behind enemy lines to retrieve a paratrooper.",
                duration_minutes=169,
                genre="War",
                rating="R",
                cast=["Tom Hanks", "Matt Damon", "Tom Sizemore", "Edward Burns"],
                director="Steven Spielberg",
                writers=["Robert Rodat"],
                producers=["Steven Spielberg", "Ian Bryce"],
                release_date=date(1998, 7, 24),
                country="USA",
                language="English",
                budget=70000000,
                revenue=481840909,
                production_company="DreamWorks Pictures",
                distributor="Paramount Pictures",
                image_url="https://image.tmdb.org/t/p/original/uqx37cS8cpHg8U35f9U5IBlrCV3.jpg",
                trailer_url="https://www.youtube.com/watch?v=zwhP5b4tD6g",
                awards=["Academy Award for Best Director", "Academy Award for Best Cinematography"],
                details={"imdb_rating": 8.6, "d_day": True}
            ),
            Movie(
                title="Raiders of the Lost Ark",
                description="In 1936, archaeologist and adventurer Indiana Jones is hired by the U.S. government to find the Ark of the Covenant.",
                duration_minutes=115,
                genre="Adventure",
                rating="PG",
                cast=["Harrison Ford", "Karen Allen", "Paul Freeman", "Ronald Lacey"],
                director="Steven Spielberg",
                writers=["Lawrence Kasdan", "George Lucas"],
                producers=["Frank Marshall"],
                release_date=date(1981, 6, 12),
                country="USA",
                language="English",
                budget=18000000,
                revenue=389925971,
                production_company="Lucasfilm Ltd.",
                distributor="Paramount Pictures",
                image_url="https://image.tmdb.org/t/p/w500/ceG9VzoRAVGwivFU403Wc3AHRys.jpg",
                trailer_url="https://www.youtube.com/watch?v=0ZOcoxjeUYo",
                awards=["Academy Award for Best Sound", "Academy Award for Best Visual Effects"],
                details={"imdb_rating": 8.4, "franchise": "Indiana Jones", "part": 1}
            ),
            Movie(
                title="The Departed",
                description="An undercover cop and a mole in the police attempt to identify each other while infiltrating an Irish gang.",
                duration_minutes=151,
                genre="Crime",
                rating="R",
                cast=["Leonardo DiCaprio", "Matt Damon", "Jack Nicholson", "Mark Wahlberg"],
                director="Martin Scorsese",
                writers=["William Monahan"],
                producers=["Brad Pitt", "Brad Grey"],
                release_date=date(2006, 10, 6),
                country="USA",
                language="English",
                budget=90000000,
                revenue=289847354,
                production_company="Warner Bros. Pictures",
                distributor="Warner Bros. Pictures",
                image_url="https://m.media-amazon.com/images/I/51mjWgQocwL._AC_.jpg",
                trailer_url="https://www.youtube.com/watch?v=iojhqm0JTW4",
                awards=["Academy Award for Best Picture", "Academy Award for Best Director"],
                details={"imdb_rating": 8.5, "remake": "Infernal Affairs"}
            ),
            Movie(
                title="City of God",
                description="In the slums of Rio, two kids' paths diverge as one struggles to become a photographer and the other a kingpin.",
                duration_minutes=130,
                genre="Crime",
                rating="R",
                cast=["Alexandre Rodrigues", "Leandro Firmino", "Phellipe Haagensen", "Douglas Silva"],
                director="Fernando Meirelles",
                writers=["Paulo Lins", "Bráulio Mantovani"],
                producers=["Andrea Barata Ribeiro", "Maurício Andrade Ramos"],
                release_date=date(2002, 8, 30),
                country="Brazil",
                language="Portuguese",
                budget=3300000,
                revenue=30641770,
                production_company="O2 Filmes",
                distributor="Miramax Films",
                image_url="https://image.tmdb.org/t/p/w500/k7eYdWvhYQyRQoU2TB2A2Xu2TfD.jpg",
                trailer_url="https://www.youtube.com/watch?v=ioUE_5wpg_E",
                awards=["Academy Award for Best Cinematography", "Golden Bear at Berlin"],
                details={"imdb_rating": 8.6, "based_on": "Paulo Lins novel"}
            ),
            Movie(
                title="Whiplash",
                description="A promising young drummer enrolls at a cut-throat music conservatory where his dreams of greatness are mentored by an instructor.",
                duration_minutes=106,
                genre="Drama",
                rating="R",
                cast=["Miles Teller", "J.K. Simmons", "Melissa Benoist", "Austin Stowell"],
                director="Damien Chazelle",
                writers=["Damien Chazelle"],
                producers=["Jason Blum", "Helen Estabrook"],
                release_date=date(2014, 10, 10),
                country="USA",
                language="English",
                budget=3300000,
                revenue=48982041,
                production_company="Bold Films",
                distributor="Sony Pictures Classics",
                image_url="https://image.tmdb.org/t/p/w500/7fn624j5lj3xTme2SgiLCeuedmO.jpg",
                trailer_url="https://www.youtube.com/watch?v=7d_jQycdQGo",
                awards=["Academy Award for Best Supporting Actor", "Academy Award for Best Film Editing"],
                details={"imdb_rating": 8.5, "music_drama": True}
            ),
            Movie(
                title="Memento",
                description="A man with short-term memory loss attempts to track down his wife's murderer.",
                duration_minutes=113,
                genre="Thriller",
                rating="R",
                cast=["Guy Pearce", "Carrie-Anne Moss", "Joe Pantoliano", "Mark Boone Junior"],
                director="Christopher Nolan",
                writers=["Christopher Nolan"],
                producers=["Suzanne Todd", "Jennifer Todd"],
                release_date=date(2000, 10, 11),
                country="USA",
                language="English",
                budget=9000000,
                revenue=39723096,
                production_company="Newmarket Capital Group",
                distributor="Newmarket Films",
                image_url="https://image.tmdb.org/t/p/w500/yuNs09hvpHVU1cBTCAk9zxsL2oW.jpg",
                trailer_url="https://www.youtube.com/watch?v=0vS0E9bBSL0",
                awards=["No major Academy Awards but critically acclaimed"],
                details={"imdb_rating": 8.4, "non_linear_narrative": True}
            ),
            Movie(
                title="The Prestige",
                description="After a tragic accident, two stage magicians engage in a battle to create the ultimate illusion.",
                duration_minutes=130,
                genre="Drama",
                rating="PG-13",
                cast=["Christian Bale", "Hugh Jackman", "Scarlett Johansson", "Michael Caine"],
                director="Christopher Nolan",
                writers=["Jonathan Nolan", "Christopher Nolan"],
                producers=["Emma Thomas", "Christopher Nolan"],
                release_date=date(2006, 10, 20),
                country="USA",
                language="English",
                budget=40000000,
                revenue=109676311,
                production_company="Warner Bros. Pictures",
                distributor="Buena Vista Pictures",
                image_url="https://onlyposter.it/cdn/shop/files/The_Prestige_2006.jpg?v=1732913780&width=823",
                trailer_url="https://www.youtube.com/watch?v=o4gHCmTQDVI",
                awards=["Academy Award for Best Cinematography"],
                details={"imdb_rating": 8.5, "based_on": "Christopher Priest novel"}
            ),
            Movie(
                title="Spirited Away",
                description="During her family's move to the suburbs, a sullen 10-year-old girl wanders into a world ruled by gods, witches, and spirits.",
                duration_minutes=125,
                genre="Animation",
                rating="PG",
                cast=["Daveigh Chase", "Suzanne Pleshette", "Miyu Irino", "Rumi Hiiragi"],
                director="Hayao Miyazaki",
                writers=["Hayao Miyazaki"],
                producers=["Toshio Suzuki"],
                release_date=date(2001, 7, 20),
                country="Japan",
                language="Japanese",
                budget=19000000,
                revenue=274925095,
                production_company="Studio Ghibli",
                distributor="Walt Disney Pictures",
                image_url="https://image.tmdb.org/t/p/w500/39wmItIWsg5sZMyRUHLkWBcuVCM.jpg",
                trailer_url="https://www.youtube.com/watch?v=ByXuk9QqQkk",
                awards=["Academy Award for Best Animated Feature", "Golden Bear at Berlin"],
                details={"imdb_rating": 8.6, "studio_ghibli": True}
            ),
            Movie(
                title="Parasite",
                description="Greed and class discrimination threaten the newly formed symbiotic relationship between the wealthy Park family and the destitute Kim clan.",
                duration_minutes=132,
                genre="Thriller",
                rating="R",
                cast=["Song Kang-ho", "Lee Sun-kyun", "Cho Yeo-jeong", "Choi Woo-shik"],
                director="Bong Joon-ho",
                writers=["Bong Joon-ho", "Han Jin-won"],
                producers=["Kwak Sin-ae", "Moon Yang-kwon"],
                release_date=date(2019, 5, 30),
                country="South Korea",
                language="Korean",
                budget=11400000,
                revenue=258799554,
                production_company="CJ Entertainment",
                distributor="CJ Entertainment",
                image_url="https://image.tmdb.org/t/p/w500/7IiTTgloJzvGI1TAYymCfbfl3vT.jpg",
                trailer_url="https://www.youtube.com/watch?v=5xH0HfJHsaY",
                awards=["Academy Award for Best Picture", "Academy Award for Best Director"],
                details={"imdb_rating": 8.5, "social_commentary": True}
            ),
            # Coming Soon Movies
            Movie(
                title="Dune: Part Two",
                description="Paul Atreides unites with Chani and the Fremen while on a path of revenge against the conspirators who destroyed his family.",
                duration_minutes=166,
                genre="Sci-Fi",
                rating="PG-13",
                cast=["Timothée Chalamet", "Zendaya", "Rebecca Ferguson", "Oscar Isaac"],
                director="Denis Villeneuve",
                writers=["Denis Villeneuve", "Jon Spaihts"],
                producers=["Mary Parent", "Cale Boyter"],
                release_date=date(2024, 3, 1),
                country="United States",
                language="English",
                budget=190000000,
                revenue=0,  # Not released yet
                production_company="Warner Bros. Pictures",
                distributor="Warner Bros. Pictures",
                image_url="https://image.tmdb.org/t/p/w500/1pdfLvkbY9ohJlCjQH2CZjjYVvJ.jpg",
                trailer_url="https://www.youtube.com/watch?v=Way9Dexny3w",
                awards=[],  # Not released yet
                details={"imdb_rating": 0, "highly_anticipated": True},
                state=MovieState.COMING_SOON
            ),
            Movie(
                title="Oppenheimer",
                description="The story of American scientist J. Robert Oppenheimer and his role in the development of the atomic bomb.",
                duration_minutes=180,
                genre="Biography",
                rating="R",
                cast=["Cillian Murphy", "Emily Blunt", "Robert Downey Jr.", "Matt Damon"],
                director="Christopher Nolan",
                writers=["Christopher Nolan"],
                producers=["Emma Thomas", "Charles Roven"],
                release_date=date(2023, 7, 21),
                country="United States",
                language="English",
                budget=100000000,
                revenue=952000000,
                production_company="Universal Pictures",
                distributor="Universal Pictures",
                image_url="https://image.tmdb.org/t/p/w500/8Gxv8gSFCU0XGDykEGv7zR1n2ua.jpg",
                trailer_url="https://www.youtube.com/watch?v=uYPbbksJxIg",
                awards=["Academy Award for Best Picture", "Academy Award for Best Director"],
                details={"imdb_rating": 8.3, "historical_drama": True},
                state=MovieState.COMING_SOON
            ),
            Movie(
                title="The Batman",
                description="When a sadistic serial killer begins murdering key political figures in Gotham, Batman is forced to investigate the city's hidden corruption.",
                duration_minutes=176,
                genre="Action",
                rating="PG-13",
                cast=["Robert Pattinson", "Zoë Kravitz", "Jeffrey Wright", "Colin Farrell"],
                director="Matt Reeves",
                writers=["Matt Reeves", "Peter Craig"],
                producers=["Dylan Clark", "Matt Reeves"],
                release_date=date(2022, 3, 4),
                country="United States",
                language="English",
                budget=185000000,
                revenue=772000000,
                production_company="Warner Bros. Pictures",
                distributor="Warner Bros. Pictures",
                image_url="https://image.tmdb.org/t/p/w500/74xTEgt7R36Fpooo50r9T25onhq.jpg",
                trailer_url="https://www.youtube.com/watch?v=mqqft2x_Aa4",
                awards=["Academy Award for Best Supporting Actor"],
                details={"imdb_rating": 7.8, "superhero": True},
                state=MovieState.COMING_SOON
            ),
            Movie(
                title="Avatar: The Way of Water",
                description="Jake Sully lives with his newfound family formed on the extrasolar moon Pandora. Once a familiar threat returns to finish what was previously started.",
                duration_minutes=192,
                genre="Sci-Fi",
                rating="PG-13",
                cast=["Sam Worthington", "Zoe Saldaña", "Sigourney Weaver", "Stephen Lang"],
                director="James Cameron",
                writers=["James Cameron", "Rick Jaffa"],
                producers=["James Cameron", "Jon Landau"],
                release_date=date(2022, 12, 16),
                country="United States",
                language="English",
                budget=350000000,
                revenue=2320000000,
                production_company="20th Century Studios",
                distributor="20th Century Studios",
                image_url="https://image.tmdb.org/t/p/w500/t6HIqrRAclMCA60NsSmeqe9RmNV.jpg",
                trailer_url="https://www.youtube.com/watch?v=d9MyW72ELq0",
                awards=["Academy Award for Best Visual Effects"],
                details={"imdb_rating": 7.6, "sequel": True},
                state=MovieState.COMING_SOON
            ),
            Movie(
                title="Top Gun: Maverick",
                description="After thirty years, Maverick is still pushing the envelope as a top naval aviator, but must confront ghosts of his past when he leads TOP GUN's elite graduates.",
                duration_minutes=130,
                genre="Action",
                rating="PG-13",
                cast=["Tom Cruise", "Miles Teller", "Jennifer Connelly", "Jon Hamm"],
                director="Joseph Kosinski",
                writers=["Ehren Kruger", "Eric Warren Singer"],
                producers=["Tom Cruise", "Christopher McQuarrie"],
                release_date=date(2022, 5, 27),
                country="United States",
                language="English",
                budget=170000000,
                revenue=1489000000,
                production_company="Paramount Pictures",
                distributor="Paramount Pictures",
                image_url="https://image.tmdb.org/t/p/w500/62HCnUTziyWcpDaBO2i1DX17ljH.jpg",
                trailer_url="https://www.youtube.com/watch?v=qSqVVswa420",
                awards=["Academy Award for Best Sound"],
                details={"imdb_rating": 8.2, "sequel": True},
                state=MovieState.COMING_SOON
            ),
            # Additional Popular Movies
            Movie(
                title="Inception",
                description="A thief who steals corporate secrets through the use of dream-sharing technology is given the inverse task of planting an idea into the mind of a C.E.O.",
                duration_minutes=148,
                genre="Sci-Fi",
                rating="PG-13",
                cast=["Leonardo DiCaprio", "Marion Cotillard", "Tom Hardy", "Elliot Page"],
                director="Christopher Nolan",
                writers=["Christopher Nolan"],
                producers=["Emma Thomas", "Christopher Nolan"],
                release_date=date(2010, 7, 16),
                country="USA",
                language="English",
                budget=160000000,
                revenue=836836967,
                production_company="Warner Bros. Pictures",
                distributor="Warner Bros. Pictures",
                image_url="https://image.tmdb.org/t/p/w500/9gk7adHYeDvHkCSEqAvQNLV5Uge.jpg",
                trailer_url="https://www.youtube.com/watch?v=YoHD9XEInc0",
                awards=["Academy Award for Best Cinematography", "Academy Award for Best Visual Effects"],
                details={"imdb_rating": 8.8, "mind_bending": True}
            ),
            Movie(
                title="The Shawshank Redemption",
                description="Two imprisoned men bond over a number of years, finding solace and eventual redemption through acts of common decency.",
                duration_minutes=142,
                genre="Drama",
                rating="R",
                cast=["Tim Robbins", "Morgan Freeman", "Bob Gunton", "William Sadler"],
                director="Frank Darabont",
                writers=["Frank Darabont"],
                producers=["Niki Marvin"],
                release_date=date(1994, 9, 23),
                country="USA",
                language="English",
                budget=25000000,
                revenue=28341469,
                production_company="Castle Rock Entertainment",
                distributor="Columbia Pictures",
                image_url="https://image.tmdb.org/t/p/w500/q6y0Go1tsGEsmtFryDOJo3dEmqu.jpg",
                trailer_url="https://www.youtube.com/watch?v=6hB3S9bIaco",
                awards=["No major Academy Awards but critically acclaimed"],
                details={"imdb_rating": 9.3, "based_on": "Stephen King novella"}
            ),
            Movie(
                title="Pulp Fiction",
                description="The lives of two mob hitmen, a boxer, a gangster and his wife intertwine in four tales of violence and redemption.",
                duration_minutes=154,
                genre="Crime",
                rating="R",
                cast=["John Travolta", "Uma Thurman", "Samuel L. Jackson", "Bruce Willis"],
                director="Quentin Tarantino",
                writers=["Quentin Tarantino"],
                producers=["Lawrence Bender"],
                release_date=date(1994, 10, 14),
                country="USA",
                language="English",
                budget=8000000,
                revenue=214179088,
                production_company="Miramax Films",
                distributor="Miramax Films",
                image_url="https://image.tmdb.org/t/p/w500/d5iIlFn5s0ImszYzBPb8JPIfbXD.jpg",
                trailer_url="https://www.youtube.com/watch?v=s7EdQ4FqbhY",
                awards=["Academy Award for Best Original Screenplay", "Palme d'Or at Cannes"],
                details={"imdb_rating": 8.9, "non_linear_narrative": True}
            ),
            Movie(
                title="The Matrix",
                description="A computer hacker learns from mysterious rebels about the true nature of his reality and his role in the war against its controllers.",
                duration_minutes=136,
                genre="Sci-Fi",
                rating="R",
                cast=["Keanu Reeves", "Laurence Fishburne", "Carrie-Anne Moss", "Hugo Weaving"],
                director="Lana Wachowski",
                writers=["Lana Wachowski", "Lilly Wachowski"],
                producers=["Joel Silver"],
                release_date=date(1999, 3, 31),
                country="USA",
                language="English",
                budget=63000000,
                revenue=467222824,
                production_company="Warner Bros. Pictures",
                distributor="Warner Bros. Pictures",
                image_url="https://image.tmdb.org/t/p/w500/f89U3ADr1oiB1s9GkdPOEpXUk5H.jpg",
                trailer_url="https://www.youtube.com/watch?v=vKQi3bBA1y8",
                awards=["Academy Award for Best Visual Effects", "Academy Award for Best Sound"],
                details={"imdb_rating": 8.7, "franchise": "The Matrix", "part": 1}
            ),
            Movie(
                title="Interstellar",
                description="A team of explorers travel through a wormhole in space in an attempt to ensure humanity's survival.",
                duration_minutes=169,
                genre="Sci-Fi",
                rating="PG-13",
                cast=["Matthew McConaughey", "Anne Hathaway", "Jessica Chastain", "Michael Caine"],
                director="Christopher Nolan",
                writers=["Jonathan Nolan", "Christopher Nolan"],
                producers=["Emma Thomas", "Christopher Nolan"],
                release_date=date(2014, 11, 7),
                country="USA",
                language="English",
                budget=165000000,
                revenue=677471339,
                production_company="Paramount Pictures",
                distributor="Warner Bros. Pictures",
                image_url="https://image.tmdb.org/t/p/w500/gEU2QniE6E77NI6lCU6MxlNBvIx.jpg",
                trailer_url="https://www.youtube.com/watch?v=zSWdZVtXT7E",
                awards=["Academy Award for Best Visual Effects"],
                details={"imdb_rating": 8.6, "space_exploration": True}
            ),
            Movie(
                title="The Godfather",
                description="The aging patriarch of an organized crime dynasty transfers control of his clandestine empire to his reluctant son.",
                duration_minutes=175,
                genre="Crime",
                rating="R",
                cast=["Marlon Brando", "Al Pacino", "James Caan", "Richard S. Castellano"],
                director="Francis Ford Coppola",
                writers=["Mario Puzo", "Francis Ford Coppola"],
                producers=["Albert S. Ruddy"],
                release_date=date(1972, 3, 24),
                country="USA",
                language="English",
                budget=6000000,
                revenue=134966411,
                production_company="Paramount Pictures",
                distributor="Paramount Pictures",
                image_url="https://image.tmdb.org/t/p/w500/3bhkrj58Vtu7enYsRolD1fZdja1.jpg",
                trailer_url="https://www.youtube.com/watch?v=sY1S34973zI",
                awards=["Academy Award for Best Picture", "Academy Award for Best Actor"],
                details={"imdb_rating": 9.2, "based_on": "Mario Puzo novel"}
            ),
            Movie(
                title="Forrest Gump",
                description="The presidencies of Kennedy and Johnson, the Vietnam War, the Watergate scandal and other historical events unfold from the perspective of an Alabama man with an IQ of 75.",
                duration_minutes=142,
                genre="Drama",
                rating="PG-13",
                cast=["Tom Hanks", "Robin Wright", "Gary Sinise", "Sally Field"],
                director="Robert Zemeckis",
                writers=["Winston Groom", "Eric Roth"],
                producers=["Wendy Finerman", "Steve Tisch"],
                release_date=date(1994, 7, 6),
                country="USA",
                language="English",
                budget=55000000,
                revenue=677387716,
                production_company="Paramount Pictures",
                distributor="Paramount Pictures",
                image_url="https://image.tmdb.org/t/p/w500/arw2vcBveWOVZr6pxd9XTd1TdQa.jpg",
                trailer_url="https://www.youtube.com/watch?v=bLvqoHBptjg",
                awards=["Academy Award for Best Picture", "Academy Award for Best Actor"],
                details={"imdb_rating": 8.8, "historical_drama": True}
            ),
            Movie(
                title="The Dark Knight",
                description="When the menace known as the Joker wreaks havoc and chaos on the people of Gotham, Batman must accept one of the greatest psychological and physical tests.",
                duration_minutes=152,
                genre="Action",
                rating="PG-13",
                cast=["Christian Bale", "Heath Ledger", "Aaron Eckhart", "Michael Caine"],
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
                awards=["Academy Award for Best Supporting Actor"],
                details={"imdb_rating": 9.0, "superhero": True}
            ),
            Movie(
                title="Fight Club",
                description="An insomniac office worker and a devil-may-care soapmaker form an underground fight club that evolves into something much, much more.",
                duration_minutes=139,
                genre="Drama",
                rating="R",
                cast=["Brad Pitt", "Edward Norton", "Helena Bonham Carter", "Meat Loaf"],
                director="David Fincher",
                writers=["Chuck Palahniuk", "Jim Uhls"],
                producers=["Art Linson", "Ceán Chaffin"],
                release_date=date(1999, 10, 15),
                country="USA",
                language="English",
                budget=63000000,
                revenue=100853753,
                production_company="20th Century Fox",
                distributor="20th Century Fox",
                image_url="https://image.tmdb.org/t/p/w500/pB8BM7pdSp6B6Ih7QZ4DrQ3PmJK.jpg",
                trailer_url="https://www.youtube.com/watch?v=BdJKm16Co6M",
                awards=["No major Academy Awards but critically acclaimed"],
                details={"imdb_rating": 8.8, "psychological_thriller": True}
            ),
            Movie(
                title="Gladiator",
                description="A former Roman General sets out to exact vengeance against the corrupt emperor who murdered his family and sent him into slavery.",
                duration_minutes=155,
                genre="Action",
                rating="R",
                cast=["Russell Crowe", "Joaquin Phoenix", "Connie Nielsen", "Oliver Reed"],
                director="Ridley Scott",
                writers=["David Franzoni", "John Logan"],
                producers=["Douglas Wick", "David Franzoni"],
                release_date=date(2000, 5, 5),
                country="USA",
                language="English",
                budget=103000000,
                revenue=460583960,
                production_company="DreamWorks Pictures",
                distributor="Universal Pictures",
                image_url="https://image.tmdb.org/t/p/w500/ty8TGRuvJLPUmAR1H1nRIsgwvim.jpg",
                trailer_url="https://www.youtube.com/watch?v=owK1qxDselE",
                awards=["Academy Award for Best Picture", "Academy Award for Best Actor"],
                details={"imdb_rating": 8.5, "historical_drama": True}
            ),
            Movie(
                title="Titanic",
                description="A seventeen-year-old aristocrat falls in love with a kind but poor artist aboard the luxurious, ill-fated R.M.S. Titanic.",
                duration_minutes=194,
                genre="Romance",
                rating="PG-13",
                cast=["Leonardo DiCaprio", "Kate Winslet", "Billy Zane", "Kathy Bates"],
                director="James Cameron",
                writers=["James Cameron"],
                producers=["James Cameron", "Jon Landau"],
                release_date=date(1997, 12, 19),
                country="USA",
                language="English",
                budget=200000000,
                revenue=2187463944,
                production_company="Paramount Pictures",
                distributor="20th Century Fox",
                image_url="https://image.tmdb.org/t/p/w500/9xjZS2rlVxm8SFx8kPC3aIGCOYQ.jpg",
                trailer_url="https://www.youtube.com/watch?v=kVrqfYjkTdQ",
                awards=["Academy Award for Best Picture", "Academy Award for Best Director"],
                details={"imdb_rating": 7.9, "historical_drama": True}
            ),
            Movie(
                title="The Avengers",
                description="Earth's mightiest heroes must come together and learn to fight as a team if they are going to stop the mischievous Loki and his alien army from enslaving humanity.",
                duration_minutes=143,
                genre="Action",
                rating="PG-13",
                cast=["Robert Downey Jr.", "Chris Evans", "Scarlett Johansson", "Jeremy Renner"],
                director="Joss Whedon",
                writers=["Joss Whedon"],
                producers=["Kevin Feige"],
                release_date=date(2012, 5, 4),
                country="USA",
                language="English",
                budget=220000000,
                revenue=1518815515,
                production_company="Marvel Studios",
                distributor="Walt Disney Pictures",
                image_url="https://image.tmdb.org/t/p/w500/RYMX2wcKCBAr24UyPD7xwmjaTn.jpg",
                trailer_url="https://www.youtube.com/watch?v=eOrNdBpGMv8",
                awards=["No major Academy Awards but critically acclaimed"],
                details={"imdb_rating": 8.0, "superhero": True, "marvel_cinematic_universe": True}
            ),
            Movie(
                title="Avatar",
                description="A paraplegic Marine dispatched to the moon Pandora on a unique mission becomes torn between following his orders and protecting the world he feels is his home.",
                duration_minutes=162,
                genre="Sci-Fi",
                rating="PG-13",
                cast=["Sam Worthington", "Zoe Saldaña", "Sigourney Weaver", "Stephen Lang"],
                director="James Cameron",
                writers=["James Cameron"],
                producers=["James Cameron", "Jon Landau"],
                release_date=date(2009, 12, 18),
                country="USA",
                language="English",
                budget=237000000,
                revenue=2923706026,
                production_company="20th Century Fox",
                distributor="20th Century Fox",
                image_url="https://image.tmdb.org/t/p/w500/jRXYjXNq0Cs2TcJjLkki24MLp7u.jpg",
                trailer_url="https://www.youtube.com/watch?v=5PSNL1qE6VY",
                awards=["Academy Award for Best Cinematography", "Academy Award for Best Visual Effects"],
                details={"imdb_rating": 7.9, "highest_grossing": True}
            ),
            Movie(
                title="The Lord of the Rings: The Fellowship of the Ring",
                description="A meek Hobbit from the Shire and eight companions set out on a journey to destroy the powerful One Ring and save Middle-earth from the Dark Lord Sauron.",
                duration_minutes=178,
                genre="Fantasy",
                rating="PG-13",
                cast=["Elijah Wood", "Ian McKellen", "Orlando Bloom", "Sean Bean"],
                director="Peter Jackson",
                writers=["J.R.R. Tolkien", "Fran Walsh"],
                producers=["Peter Jackson", "Fran Walsh"],
                release_date=date(2001, 12, 19),
                country="New Zealand",
                language="English",
                budget=93000000,
                revenue=897690072,
                production_company="New Line Cinema",
                distributor="New Line Cinema",
                image_url="https://image.tmdb.org/t/p/w500/6oom5QYQ2yQTMJIbnvbkBL9cHo6.jpg",
                trailer_url="https://www.youtube.com/watch?v=V75dMMIW2B4",
                awards=["Academy Award for Best Cinematography", "Academy Award for Best Original Score"],
                details={"imdb_rating": 8.8, "based_on": "J.R.R. Tolkien novel", "franchise": "The Lord of the Rings"}
            ),
            Movie(
                title="Star Wars: Episode IV - A New Hope",
                description="Luke Skywalker joins forces with a Jedi Knight, a cocky pilot, a Wookiee and two droids to save the galaxy from the Empire's world-destroying battle station.",
                duration_minutes=121,
                genre="Sci-Fi",
                rating="PG",
                cast=["Mark Hamill", "Harrison Ford", "Carrie Fisher", "Alec Guinness"],
                director="George Lucas",
                writers=["George Lucas"],
                producers=["Gary Kurtz"],
                release_date=date(1977, 5, 25),
                country="USA",
                language="English",
                budget=11000000,
                revenue=775398007,
                production_company="Lucasfilm Ltd.",
                distributor="20th Century Fox",
                image_url="https://image.tmdb.org/t/p/w500/6FfCtAuVAW8XJjZ7eWeLibRLWTw.jpg",
                trailer_url="https://www.youtube.com/watch?v=1g3_CFmnU7k",
                awards=["Academy Award for Best Visual Effects", "Academy Award for Best Original Score"],
                details={"imdb_rating": 8.6, "franchise": "Star Wars", "part": 4}
            ),
            Movie(
                title="Back to the Future",
                description="Marty McFly, a 17-year-old high school student, is accidentally sent thirty years into the past in a time-traveling DeLorean invented by his close friend, the eccentric scientist Doc Brown.",
                duration_minutes=116,
                genre="Sci-Fi",
                rating="PG",
                cast=["Michael J. Fox", "Christopher Lloyd", "Lea Thompson", "Crispin Glover"],
                director="Robert Zemeckis",
                writers=["Robert Zemeckis", "Bob Gale"],
                producers=["Neil Canton", "Bob Gale"],
                release_date=date(1985, 7, 3),
                country="USA",
                language="English",
                budget=19000000,
                revenue=381109762,
                production_company="Universal Pictures",
                distributor="Universal Pictures",
                image_url="https://image.tmdb.org/t/p/w500/7lyBcpYB0Qt8gYhXYaEZUNlNQAv.jpg",
                trailer_url="https://www.youtube.com/watch?v=qvsgGtivCgs",
                awards=["Academy Award for Best Sound Effects Editing"],
                details={"imdb_rating": 8.5, "time_travel": True}
            ),
            Movie(
                title="The Silence of the Lambs",
                description="A young F.B.I. cadet must receive the help of an incarcerated and manipulative cannibal killer to help catch another serial killer, a madman who skins his victims.",
                duration_minutes=118,
                genre="Thriller",
                rating="R",
                cast=["Jodie Foster", "Anthony Hopkins", "Lawrence A. Bonney", "Kasi Lemmons"],
                director="Jonathan Demme",
                writers=["Thomas Harris", "Ted Tally"],
                producers=["Edward Saxon", "Kenneth Utt"],
                release_date=date(1991, 2, 14),
                country="USA",
                language="English",
                budget=19000000,
                revenue=272742922,
                production_company="Orion Pictures",
                distributor="Orion Pictures",
                image_url="https://image.tmdb.org/t/p/w500/uS9m8OBk1A8eM9I042bx8XXpqAq.jpg",
                trailer_url="https://www.youtube.com/watch?v=W6Mm8Sbe__o",
                awards=["Academy Award for Best Picture", "Academy Award for Best Actor"],
                details={"imdb_rating": 8.6, "psychological_thriller": True}
            ),
            Movie(
                title="Goodfellas",
                description="The story of Henry Hill and his life in the mob, covering his relationship with his wife Karen Hill and his mob partners.",
                duration_minutes=146,
                genre="Crime",
                rating="R",
                cast=["Robert De Niro", "Ray Liotta", "Joe Pesci", "Lorraine Bracco"],
                director="Martin Scorsese",
                writers=["Nicholas Pileggi", "Martin Scorsese"],
                producers=["Irwin Winkler"],
                release_date=date(1990, 9, 21),
                country="USA",
                language="English",
                budget=25000000,
                revenue=46836394,
                production_company="Warner Bros. Pictures",
                distributor="Warner Bros. Pictures",
                image_url="https://image.tmdb.org/t/p/w500/aKuFiU82s5ISJpGZp7YkIr3kCUd.jpg",
                trailer_url="https://www.youtube.com/watch?v=qo5jJpHtI1Y",
                awards=["Academy Award for Best Supporting Actor"],
                details={"imdb_rating": 8.7, "based_on": "Nicholas Pileggi book"}
            ),
            Movie(
                title="Braveheart",
                description="Scottish warrior William Wallace leads his countrymen in a rebellion to free his homeland from the tyranny of King Edward I of England.",
                duration_minutes=178,
                genre="Action",
                rating="R",
                cast=["Mel Gibson", "Sophie Marceau", "Patrick McGoohan", "Angus Macfadyen"],
                director="Mel Gibson",
                writers=["Randall Wallace"],
                producers=["Mel Gibson", "Alan Ladd Jr."],
                release_date=date(1995, 5, 24),
                country="USA",
                language="English",
                budget=72000000,
                revenue=210409989,
                production_company="Paramount Pictures",
                distributor="Paramount Pictures",
                image_url="https://image.tmdb.org/t/p/w500/2qAgGeYdLjelOEqjW9FYvPHpplC.jpg",
                trailer_url="https://www.youtube.com/watch?v=nMft5QDOHvk",
                awards=["Academy Award for Best Picture", "Academy Award for Best Director"],
                details={"imdb_rating": 8.3, "historical_drama": True}
            ),
            # Additional Current and Recent Movies
            Movie(
                title="Wonka",
                description="A young Willy Wonka embarks on a magical but turbulent journey through the Chocolate Factory in this prequel to Charlie and the Chocolate Factory.",
                duration_minutes=160,
                genre="Fantasy",
                rating="PG",
                cast=["Timothée Chalamet", "Calah Lane", "Keegan-Michael Key", "Olivia Colman"],
                director="Paul King",
                writers=["Simon Farnaby", "Paul King"],
                producers=["David Heyman", "Michael Siegel"],
                release_date=date(2023, 12, 15),
                country="USA",
                language="English",
                budget=125000000,
                revenue=580000000,
                production_company="Warner Bros. Pictures",
                distributor="Warner Bros. Pictures",
                image_url="https://m.media-amazon.com/images/I/81fCjzKaBTL._AC_SL1500_.jpg",
                trailer_url="https://www.youtube.com/watch?v=wYU4PNztdPo",
                awards=["Golden Globe for Best Motion Picture"],
                details={"imdb_rating": 7.1, "musical": True}
            ),
            Movie(
                title="The Holdovers",
                description="A curmudgeonly instructor at a prep school is forced to chaperone the school's most incorrigible students on a holiday break.",
                duration_minutes=133,
                genre="Comedy",
                rating="R",
                cast=["Paul Giamatti", "Dominic Sessa", "Da'Vine Joy Randolph", "Carrie Preston"],
                director="Alexander Payne",
                writers=["David Hemingson"],
                producers=["Mark Johnson", "Bill Block"],
                release_date=date(2023, 10, 27),
                country="USA",
                language="English",
                budget=0,
                revenue=45000000,
                production_company="Focus Features",
                distributor="Focus Features",
                image_url="https://image.tmdb.org/t/p/w500/VHSzNBTwxV8vh7wylo7O9CLdac.jpg",
                trailer_url="https://www.youtube.com/watch?v=AJO0B9JQ0zg",
                awards=["Academy Award for Best Picture", "Golden Globe for Best Motion Picture"],
                details={"imdb_rating": 8.0, "coming_of_age": True}
            ),
            Movie(
                title="Poor Things",
                description="Brought back to life by an unorthodox scientist, a young woman runs off with a debauched lawyer on a whirlwind adventure.",
                duration_minutes=141,
                genre="Comedy",
                rating="R",
                cast=["Emma Stone", "Mark Ruffalo", "Willem Dafoe", "Ramy Youssef"],
                director="Yorgos Lanthimos",
                writers=["Tony McNamara"],
                producers=["Ed Guiney", "Andrew Lowe"],
                release_date=date(2023, 12, 8),
                country="Ireland",
                language="English",
                budget=35000000,
                revenue=108000000,
                production_company="Element Pictures",
                distributor="Searchlight Pictures",
                image_url="https://image.tmdb.org/t/p/w500/kCGlIMHnOm8JPXq3rXM6c5wMxcT.jpg",
                trailer_url="https://www.youtube.com/watch?v=RlbR5N6veqw",
                awards=["Academy Award for Best Actress", "Golden Lion at Venice"],
                details={"imdb_rating": 8.1, "surreal": True}
            ),
            Movie(
                title="Anatomy of a Fall",
                description="A woman's life is turned upside down when her husband dies in what appears to be an accident, forcing her to defend herself in court.",
                duration_minutes=151,
                genre="Thriller",
                rating="R",
                cast=["Sandra Hüller", "Swann Arlaud", "Milo Machado-Graner", "Antoine Reinartz"],
                director="Justine Triet",
                writers=["Justine Triet", "Arthur Harari"],
                producers=["Marie-Ange Luciani", "David Thion"],
                release_date=date(2023, 8, 23),
                country="France",
                language="French",
                budget=0,
                revenue=20000000,
                production_company="Les Films Pelléas",
                distributor="Neon",
                image_url="https://image.tmdb.org/t/p/w500/kQs6keheMwCxJxrzV83VUwFtHkB.jpg",
                trailer_url="https://www.youtube.com/watch?v=0iYrQ9TDtvc",
                awards=["Palme d'Or at Cannes", "Academy Award for Best Original Screenplay"],
                details={"imdb_rating": 7.7, "courtroom_drama": True}
            ),
            Movie(
                title="Barbie",
                description="Barbie and Ken are having the time of their lives in the colorful and seemingly perfect world of Barbie Land, but when they get a chance to go to the real world, they soon discover the joys and perils of living among humans.",
                duration_minutes=114,
                genre="Comedy",
                rating="PG-13",
                cast=["Margot Robbie", "Ryan Gosling", "Issa Rae", "Kate McKinnon"],
                director="Greta Gerwig",
                writers=["Greta Gerwig", "Noah Baumbach"],
                producers=["David Heyman", "Margot Robbie"],
                release_date=date(2023, 7, 21),
                country="USA",
                language="English",
                budget=145000000,
                revenue=1440000000,
                production_company="Warner Bros. Pictures",
                distributor="Warner Bros. Pictures",
                image_url="https://image.tmdb.org/t/p/w500/iuFNMS8U5cb6xfzi51Dbkovj7vM.jpg",
                trailer_url="https://www.youtube.com/watch?v=pBk4NYhWNMM",
                awards=["Golden Globe for Best Motion Picture"],
                details={"imdb_rating": 6.9, "highest_grossing_2023": True}
            ),
            Movie(
                title="Oppenheimer",
                description="The story of American scientist J. Robert Oppenheimer and his role in the development of the atomic bomb.",
                duration_minutes=180,
                genre="Biography",
                rating="R",
                cast=["Cillian Murphy", "Emily Blunt", "Robert Downey Jr.", "Matt Damon"],
                director="Christopher Nolan",
                writers=["Christopher Nolan"],
                producers=["Emma Thomas", "Charles Roven"],
                release_date=date(2023, 7, 21),
                country="United States",
                language="English",
                budget=100000000,
                revenue=952000000,
                production_company="Universal Pictures",
                distributor="Universal Pictures",
                image_url="https://image.tmdb.org/t/p/w500/8Gxv8gSFCU0XGDykEGv7zR1n2ua.jpg",
                trailer_url="https://www.youtube.com/watch?v=uYPbbksJxIg",
                awards=["Academy Award for Best Picture", "Academy Award for Best Director"],
                details={"imdb_rating": 8.3, "historical_drama": True}
            ),
            Movie(
                title="Dune: Part Two",
                description="Paul Atreides unites with Chani and the Fremen while on a path of revenge against the conspirators who destroyed his family.",
                duration_minutes=166,
                genre="Sci-Fi",
                rating="PG-13",
                cast=["Timothée Chalamet", "Zendaya", "Rebecca Ferguson", "Oscar Isaac"],
                director="Denis Villeneuve",
                writers=["Denis Villeneuve", "Jon Spaihts"],
                producers=["Mary Parent", "Cale Boyter"],
                release_date=date(2024, 3, 1),
                country="United States",
                language="English",
                budget=190000000,
                revenue=711844167,
                production_company="Warner Bros. Pictures",
                distributor="Warner Bros. Pictures",
                image_url="https://image.tmdb.org/t/p/w500/1pdfLvkbY9ohJlCjQH2CZjjYVvJ.jpg",
                trailer_url="https://www.youtube.com/watch?v=Way9Dexny3w",
                awards=["Academy Award for Best Visual Effects"],
                details={"imdb_rating": 8.5, "highly_anticipated": True}
            ),
            Movie(
                title="Challengers",
                description="Tashi, a former tennis prodigy turned coach, turned her husband into a champion. But to overcome a losing streak, she recruits the help of an old acquaintance and ignites a rivalry between him and her husband.",
                duration_minutes=131,
                genre="Drama",
                rating="R",
                cast=["Zendaya", "Mike Faist", "Josh O'Connor", "Aidan Quinn"],
                director="Luca Guadagnino",
                writers=["Justin Kuritzkes"],
                producers=["Amy Pascal", "Luca Guadagnino"],
                release_date=date(2024, 4, 26),
                country="USA",
                language="English",
                budget=55000000,
                revenue=95000000,
                production_company="Metro-Goldwyn-Mayer",
                distributor="Amazon MGM Studios",
                image_url="https://image.tmdb.org/t/p/w500/H6vke7zGiuLsz4v4RPeReb9rsv.jpg",
                trailer_url="https://www.youtube.com/watch?v=44LdLqgOpjo",
                awards=["No major Academy Awards but critically acclaimed"],
                details={"imdb_rating": 7.2, "sports_drama": True}
            ),
            Movie(
                title="Ghostbusters: Frozen Empire",
                description="When the discovery of an ancient artifact unleashes an evil force, Ghostbusters new and old must join forces to protect their home and save the world from a second ice age.",
                duration_minutes=115,
                genre="Comedy",
                rating="PG-13",
                cast=["Paul Rudd", "Carrie Coon", "Finn Wolfhard", "Mckenna Grace"],
                director="Gil Kenan",
                writers=["Jason Reitman", "Gil Kenan"],
                producers=["Jason Reitman", "Jason Blumenfeld"],
                release_date=date(2024, 3, 22),
                country="USA",
                language="English",
                budget=100000000,
                revenue=202000000,
                production_company="Columbia Pictures",
                distributor="Sony Pictures",
                image_url="https://en.wikipedia.org/wiki/Ghostbusters:_Frozen_Empire#/media/File:Ghostbusters_(2024)_poster.jpg",
                trailer_url="https://www.youtube.com/watch?v=dSJNs6qaRfQ",
                awards=["No major Academy Awards"],
                details={"imdb_rating": 6.1, "franchise": "Ghostbusters"}
            ),
            Movie(
                title="Monkey Man",
                description="An anonymous young man unleashes a campaign of vengeance against the corrupt leaders who murdered his mother and continue to systematically victimize the poor and powerless.",
                duration_minutes=121,
                genre="Action",
                rating="R",
                cast=["Dev Patel", "Sharlto Copley", "Pitobash", "Vipin Sharma"],
                director="Dev Patel",
                writers=["Dev Patel", "Paul Angunawela"],
                producers=["Dev Patel", "Jordan Peele"],
                release_date=date(2024, 4, 5),
                country="USA",
                language="English",
                budget=10000000,
                revenue=33000000,
                production_company="Bron Studios",
                distributor="Universal Pictures",
                image_url="https://image.tmdb.org/t/p/w500/4lhR4L2vzzjl68P1zJyCH755Oz4.jpg",
                trailer_url="https://www.youtube.com/watch?v=g-W0fHzQb2A",
                awards=["No major Academy Awards but critically acclaimed"],
                details={"imdb_rating": 7.0, "action_drama": True}
            ),
            Movie(
                title="Love Lies Bleeding",
                description="Reclusive gym manager Lou falls hard for Jackie, an ambitious bodybuilder headed through town to Las Vegas in pursuit of her dream. But their love ignites violence, pulling them deep into the web of Lou's criminal family.",
                duration_minutes=104,
                genre="Thriller",
                rating="R",
                cast=["Kristen Stewart", "Katy O'Brian", "Ed Harris", "Dave Franco"],
                director="Rose Glass",
                writers=["Weronika Tofilska", "Rose Glass"],
                producers=["Andrea Cornwell", "Oliver Kassman"],
                release_date=date(2024, 3, 8),
                country="UK",
                language="English",
                budget=0,
                revenue=8000000,
                production_company="A24",
                distributor="A24",
                image_url="https://www.classificationoffice.govt.nz/media/images/love_lies_bleeding_poster.width-1200.jpg",
                trailer_url="https://www.youtube.com/watch?v=2z-5XaS3fEw",
                awards=["No major Academy Awards but critically acclaimed"],
                details={"imdb_rating": 6.7, "neo_noir": True}
            ),
            Movie(
                title="Civil War",
                description="A journey across a dystopian future America, following a team of military-embedded journalists as they race against time to reach DC before rebel factions descend upon the White House.",
                duration_minutes=109,
                genre="Action",
                rating="R",
                cast=["Kirsten Dunst", "Wagner Moura", "Cailee Spaeny", "Stephen McKinley Henderson"],
                director="Alex Garland",
                writers=["Alex Garland"],
                producers=["Andrew Macdonald", "Allon Reich"],
                release_date=date(2024, 4, 12),
                country="UK",
                language="English",
                budget=50000000,
                revenue=122000000,
                production_company="A24",
                distributor="A24",
                image_url="https://flightstightsandmovienights.com/wp-content/uploads/2016/05/captain-america-civil-war.jpg",
                trailer_url="https://www.youtube.com/watch?v=Qf1RJm9QiBA",
                awards=["No major Academy Awards but critically acclaimed"],
                details={"imdb_rating": 7.0, "dystopian": True}
            ),
            Movie(
                title="Drive-Away Dolls",
                description="Jamie, an uninhibited free spirit and her uptight best friend Marian find themselves in a bizarre predicament after a night out that goes wrong. Marian's larcenous aunt has died and left her a run-down New Jersey motel.",
                duration_minutes=84,
                genre="Comedy",
                rating="R",
                cast=["Margaret Qualley", "Geraldine Viswanathan", "Beanie Feldstein", "Joanna Arnow"],
                director="Ethan Coen",
                writers=["Ethan Coen", "Tricia Cooke"],
                producers=["Ethan Coen", "Tricia Cooke"],
                release_date=date(2024, 2, 23),
                country="USA",
                language="English",
                budget=0,
                revenue=7000000,
                production_company="Focus Features",
                distributor="Focus Features",
                image_url="https://image.tmdb.org/t/p/w500/gavGnAMT3OA9Ib3oTI7Zf1aX0qb.jpg",
                trailer_url="https://www.youtube.com/watch?v=YPfKCPxyFW0",
                awards=["No major Academy Awards"],
                details={"imdb_rating": 5.6, "road_trip_comedy": True}
            ),
            Movie(
                title="Dune",
                description="Paul Atreides, a brilliant and gifted young man born into a great destiny beyond his understanding, must travel to the most dangerous planet in the universe to ensure the future of his family and his people.",
                duration_minutes=155,
                genre="Sci-Fi",
                rating="PG-13",
                cast=["Timothée Chalamet", "Rebecca Ferguson", "Oscar Isaac", "Jason Momoa"],
                director="Denis Villeneuve",
                writers=["Jon Spaihts", "Denis Villeneuve"],
                producers=["Mary Parent", "Cale Boyter"],
                release_date=date(2021, 10, 22),
                country="USA",
                language="English",
                budget=165000000,
                revenue=401000000,
                production_company="Warner Bros. Pictures",
                distributor="Warner Bros. Pictures",
                image_url="https://image.tmdb.org/t/p/w500/d5NXSklXo0qyIYkgV94XAgMIckC.jpg",
                trailer_url="https://www.youtube.com/watch?v=n9xhJrPXop4",
                awards=["Academy Award for Best Cinematography", "Academy Award for Best Original Score"],
                details={"imdb_rating": 8.0, "epic": True}
            ),
            Movie(
                title="Everything Everywhere All at Once",
                description="A middle-aged Chinese immigrant is swept up into an insane adventure in which she alone can save existence by exploring other universes and connecting with the lives she could have led.",
                duration_minutes=139,
                genre="Action",
                rating="R",
                cast=["Michelle Yeoh", "Stephanie Hsu", "Jamie Lee Curtis", "Tallie Medel"],
                director="Daniels",
                writers=["Daniels"],
                producers=["Anthony Russo", "Joe Russo"],
                release_date=date(2022, 4, 8),
                country="USA",
                language="English",
                budget=25000000,
                revenue=143000000,
                production_company="A24",
                distributor="A24",
                image_url="https://image.tmdb.org/t/p/w500/w3LxiVYdWWRvEVdn5RYq6jIqkb1.jpg",
                trailer_url="https://www.youtube.com/watch?v=wxN1T1uxQ2g",
                awards=["Academy Award for Best Picture", "Academy Award for Best Director"],
                details={"imdb_rating": 7.8, "multiverse": True}
            ),
            Movie(
                title="The Menu",
                description="A young couple travels to a remote island to eat at an exclusive restaurant where the chef has prepared a lavish menu, with some shocking surprises.",
                duration_minutes=107,
                genre="Thriller",
                rating="R",
                cast=["Ralph Fiennes", "Anya Taylor-Joy", "Nicholas Hoult", "Hong Chau"],
                director="Mark Mylod",
                writers=["Seth Reiss", "Will Tracy"],
                producers=["Adam McKay", "Kevin J. Messick"],
                release_date=date(2022, 11, 18),
                country="USA",
                language="English",
                budget=35000000,
                revenue=78000000,
                production_company="Searchlight Pictures",
                distributor="Searchlight Pictures",
                image_url="https://www.robertmitchellevans.com/wp-content/uploads/2022/12/1-1-The-Menu.jpeg",
                trailer_url="https://www.youtube.com/watch?v=C_uTkUGcHv4",
                awards=["No major Academy Awards but critically acclaimed"],
                details={"imdb_rating": 7.2, "dark_comedy": True}
            ),
            Movie(
                title="Bullet Train",
                description="Five assassins aboard a fast moving bullet train find out their missions have something in common.",
                duration_minutes=127,
                genre="Action",
                rating="R",
                cast=["Brad Pitt", "Joey King", "Aaron Taylor-Johnson", "Brian Tyree Henry"],
                director="David Leitch",
                writers=["Zak Olkewicz"],
                producers=["Antoine Fuqua", "David Leitch"],
                release_date=date(2022, 8, 5),
                country="USA",
                language="English",
                budget=85900000,
                revenue=239000000,
                production_company="Columbia Pictures",
                distributor="Sony Pictures",
                image_url="https://m.media-amazon.com/images/I/71IXxbU87-L._AC_UF894,1000_QL80_.jpg",
                trailer_url="https://www.youtube.com/watch?v=0IOsk2Vlc4o",
                awards=["No major Academy Awards"],
                details={"imdb_rating": 7.3, "action_comedy": True}
            ),
            Movie(
                title="Don't Look Up",
                description="Two low-level astronomers must go on a giant media tour to warn mankind of an approaching comet that will destroy planet Earth.",
                duration_minutes=138,
                genre="Comedy",
                rating="R",
                cast=["Leonardo DiCaprio", "Jennifer Lawrence", "Meryl Streep", "Cate Blanchett"],
                director="Adam McKay",
                writers=["Adam McKay"],
                producers=["Adam McKay", "Kevin J. Messick"],
                release_date=date(2021, 12, 24),
                country="USA",
                language="English",
                budget=75000000,
                revenue=790000,
                production_company="Netflix",
                distributor="Netflix",
                image_url="https://image.tmdb.org/t/p/w500/th4E1yqsE8DGpAseLiUrI60Hf8V.jpg",
                trailer_url="https://www.youtube.com/watch?v=RbIxYm3mKzI",
                awards=["Golden Globe for Best Motion Picture"],
                details={"imdb_rating": 7.2, "satire": True}
            ),
            Movie(
                title="The Power of the Dog",
                description="Charismatic rancher Phil Burbank inspires fear and awe in those around him. When his brother brings home a new wife and her son, Phil torments them until he finds himself exposed to the possibility of love.",
                duration_minutes=126,
                genre="Drama",
                rating="R",
                cast=["Benedict Cumberbatch", "Kirsten Dunst", "Jesse Plemons", "Kodi Smit-McPhee"],
                director="Jane Campion",
                writers=["Jane Campion"],
                producers=["Tanya Seghatchian", "Emile Sherman"],
                release_date=date(2021, 11, 17),
                country="New Zealand",
                language="English",
                budget=35000000,
                revenue=3000000,
                production_company="See-Saw Films",
                distributor="Netflix",
                image_url="https://framerusercontent.com/images/JmuVjLFmJNGXYKMUi4aGvaAIDhc.png?scale-down-to=1024",
                trailer_url="https://www.youtube.com/watch?v=LRDPo0CHrko",
                awards=["Academy Award for Best Director", "Academy Award for Best Supporting Actor"],
                details={"imdb_rating": 6.8, "western_drama": True}
            ),
            Movie(
                title="No Time to Die",
                description="James Bond has left active service. His peace is short-lived when Felix Leiter, an old friend from the CIA, turns up asking for help, leading Bond onto the trail of a mysterious villain armed with dangerous new technology.",
                duration_minutes=163,
                genre="Action",
                rating="PG-13",
                cast=["Daniel Craig", "Ana de Armas", "Rami Malek", "Léa Seydoux"],
                director="Cary Joji Fukunaga",
                writers=["Neal Purvis", "Robert Wade"],
                producers=["Barbara Broccoli", "Michael G. Wilson"],
                release_date=date(2021, 10, 8),
                country="UK",
                language="English",
                budget=250000000,
                revenue=774000000,
                production_company="Eon Productions",
                distributor="MGM/UA",
                image_url="https://images-cdn.ubuy.co.id/636b04c3114c9d4a86576c33-no-time-to-die-james-bond-007-movie.jpgsssssssssssss",
                trailer_url="https://www.youtube.com/watch?v=vw2FOYjCz38",
                awards=["Academy Award for Best Original Song"],
                details={"imdb_rating": 7.3, "franchise": "James Bond"}
            )
        ]
        
        for movie in movies:
            session.add(movie)
        session.commit()
        
        for movie in movies:
            # Create cast entries with real profile images
            cast_profiles = {
                # Original cast
                "Song Kang-ho": "https://image.tmdb.org/t/p/w185/7dw9wIpFZ5nJZ3zqrue8t7hUUgQ.jpg",
                "Lee Sun-kyun": "https://image.tmdb.org/t/p/w185/nHFBbSFohzOUOvMxPVwe3Es2nJw.jpg",
                "Cho Yeo-jeong": "https://image.tmdb.org/t/p/w185/5MgWM8pkUiYkj9MEaEpO0Ir1FD9.jpg",
                "Choi Woo-shik": "https://image.tmdb.org/t/p/w185/hRDiuKWwe156zRjEu826eci7H3r.jpg",
                "Daveigh Chase": "https://image.tmdb.org/t/p/w185/3PVQPEc6nXNX2eoW2UbsfVikc7H.jpg",
                "Suzanne Pleshette": "https://image.tmdb.org/t/p/w185/vSuO3CnNkoCefZVTpCARNfJPYhr.jpg",
                "Miyu Irino": "https://image.tmdb.org/t/p/w185/8qEEhHUObNvGQr4e6eqLu5z4qTz.jpg",
                "Rumi Hiiragi": "https://image.tmdb.org/t/p/w185/zITaVtFyc4xSM3mxSoPRWHbqgJI.jpg",
                "Leonardo DiCaprio": "https://image.tmdb.org/t/p/w185/wo2hJpn04vbtmh0B9utCFdsQhxM.jpg",
                "Joseph Gordon-Levitt": "https://image.tmdb.org/t/p/w185/6O6FhJZH5V3BzHfS4kHNJ8pN.jpg",
                "Christian Bale": "https://image.tmdb.org/t/p/w185/1Gj2xYf6Pe4QkJDfKmY7WqeK.jpg",
                "Heath Ledger": "https://image.tmdb.org/t/p/w185/5Y9HnYYa9jF4NunY9lSgJGjSe8E.jpg",
                "Tom Cruise": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "Miles Teller": "https://image.tmdb.org/t/p/w185/8u8Z7T3h3l2VgBRHqpWJgKJj4rZ.jpg",
                "Jennifer Connelly": "https://image.tmdb.org/t/p/w185/zY4Y8RNQ2KGfQ8a1fX2EiQJnO9.jpg",
                "Jon Hamm": "https://image.tmdb.org/t/p/w185/kzLxyUYxPZeGVXeO3KNi9oN8i8.jpg",
                "Timothée Chalamet": "https://image.tmdb.org/t/p/w185/BE2sdjpgsa2rNTFa66f7upkaOP.jpg",
                "Zendaya": "https://image.tmdb.org/t/p/w185/9u3Y2Hd7UTmVTnGD0dYPx4oXBn.jpg",
                "Rebecca Ferguson": "https://image.tmdb.org/t/p/w185/lJloQh0UO7C4i3Cz7npFKB1WLKm.jpg",
                "Oscar Isaac": "https://image.tmdb.org/t/p/w185/dW5U5yrIIPmMjRThR9KT2xH6nTz.jpg",
                "Cillian Murphy": "https://image.tmdb.org/t/p/w185/lldeQ91GwIVff43JBrpdbAAeYWj.jpg",
                "Emily Blunt": "https://image.tmdb.org/t/p/w185/nCjjHPNwRn2CNJF9oR0TKrwn9cL.jpg",
                "Robert Downey Jr.": "https://image.tmdb.org/t/p/w185/im9SAqJPZKEbVZGmjXuLI4O7RvM.jpg",
                "Matt Damon": "https://image.tmdb.org/t/p/w185/elSlNgV8xVifsbHpFsqrPGxJToZ.jpg",
                "Robert Pattinson": "https://image.tmdb.org/t/p/w185/kU3B75TyRiCgE270EyZnHjfivoq.jpg",
                "Zoë Kravitz": "https://image.tmdb.org/t/p/w185/7rvpB2gTszDyrQHfKQ8Td0xDXp.jpg",
                "Jeffrey Wright": "https://image.tmdb.org/t/p/w185/z2vaNT0Dzdsp4KGGJv8VNPTXNew.jpg",
                "Colin Farrell": "https://image.tmdb.org/t/p/w185/7BZM4WZaOsM8Rh7lGZO9BF5e4y9.jpg",
                "Sam Worthington": "https://image.tmdb.org/t/p/w185/9WqPgI8hkSvQKQhgV6dOoK8E9K.jpg",
                "Zoe Saldaña": "https://image.tmdb.org/t/p/w185/ofNrWiA2KDdqiNxFTLp51HcXUlp.jpg",
                "Sigourney Weaver": "https://image.tmdb.org/t/p/w185/7dG2PnD8OeC6VU4eC3LKR8HqBJb.jpg",
                "Stephen Lang": "https://image.tmdb.org/t/p/w185/8Z7Y4E2m1T0X7jY3Q4Y5Z6W7X8Y.jpg",
                # New cast members for expanded movies
                "Marion Cotillard": "https://image.tmdb.org/t/p/w185/7pjlyC6ZEHq5zT83Ezr8GgJVLr5.jpg",
                "Tom Hardy": "https://image.tmdb.org/t/p/w185/yVGF9FvDxTDPhGimTbZNfghpllW.jpg",
                "Elliot Page": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",  # Updated name
                "Tim Robbins": "https://image.tmdb.org/t/p/w185/6tEfTQFVJQvWyO7eHkPqkHQzDy.jpg",
                "Bob Gunton": "https://image.tmdb.org/t/p/w185/4Z0Z0Z0Z0Z0Z0Z0Z0Z0Z0Z0Z0Z0.jpg",
                "William Sadler": "https://image.tmdb.org/t/p/w185/5Y9HnYYa9jF4NunY9lSgJGjSe8E.jpg",
                "John Travolta": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "Uma Thurman": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "Samuel L. Jackson": "https://image.tmdb.org/t/p/w185/nCjjHPNwRn2CNJF9oR0TKrwn9cL.jpg",
                "Bruce Willis": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "Keanu Reeves": "https://image.tmdb.org/t/p/w185/cgoy7t5Ve075naBPcewZrc3q2xT.jpg",
                "Laurence Fishburne": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "Carrie-Anne Moss": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "Hugo Weaving": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "Matthew McConaughey": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "Anne Hathaway": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "Jessica Chastain": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "Marlon Brando": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "Al Pacino": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "James Caan": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "Richard S. Castellano": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "Robin Wright": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "Gary Sinise": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "Sally Field": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "Aaron Eckhart": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "Edward Norton": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "Helena Bonham Carter": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "Meat Loaf": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "Russell Crowe": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "Joaquin Phoenix": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "Connie Nielsen": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "Oliver Reed": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "Kate Winslet": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "Billy Zane": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "Kathy Bates": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "Chris Evans": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "Scarlett Johansson": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "Jeremy Renner": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "Elijah Wood": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "Ian McKellen": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "Orlando Bloom": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "Sean Bean": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "Mark Hamill": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "Harrison Ford": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "Carrie Fisher": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "Alec Guinness": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "Michael J. Fox": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "Christopher Lloyd": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "Lea Thompson": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "Crispin Glover": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "Jodie Foster": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "Anthony Hopkins": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "Lawrence A. Bonney": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "Kasi Lemmons": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "Robert De Niro": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "Ray Liotta": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "Joe Pesci": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "Lorraine Bracco": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "Mel Gibson": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "Sophie Marceau": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "Patrick McGoohan": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "Angus Macfadyen": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                # Add more for other movies
                "Brad Pitt": "https://image.tmdb.org/t/p/w185/kU3B75TyRiCgE270EyZnHjfivoq.jpg",
                "Morgan Freeman": "https://image.tmdb.org/t/p/w185/oIciQWr8VwKoR8TmAw1owaiZFyb.jpg",
                "Gwyneth Paltrow": "https://image.tmdb.org/t/p/w185/8Z7Y4E2m1T0X7jY3Q4Y5Z6W7X8Y.jpg",
                "Kevin Spacey": "https://image.tmdb.org/t/p/w185/8Z7Y4E2m1T0X7jY3Q4Y5Z6W7X8Y.jpg",
                "Tom Hanks": "https://image.tmdb.org/t/p/w185/xndWFsBlClOJYTdZv1ixVst2VUI.jpg",
                "Michael Clarke Duncan": "https://image.tmdb.org/t/p/w185/8Z7Y4E2m1T0X7jY3Q4Y5Z6W7X8Y.jpg",
                "David Morse": "https://image.tmdb.org/t/p/w185/8Z7Y4E2m1T0X7jY3Q4Y5Z6W7X8Y.jpg",
                "Bonnie Hunt": "https://image.tmdb.org/t/p/w185/8Z7Y4E2m1T0X7jY3Q4Y5Z6W7X8Y.jpg",
                "Annette Bening": "https://image.tmdb.org/t/p/w185/8Z7Y4E2m1T0X7jY3Q4Y5Z6W7X8Y.jpg",
                "Thora Birch": "https://image.tmdb.org/t/p/w185/8Z7Y4E2m1T0X7jY3Q4Y5Z6W7X8Y.jpg",
                "Wes Bentley": "https://image.tmdb.org/t/p/w185/8Z7Y4E2m1T0X7jY3Q4Y5Z6W7X8Y.jpg",
                "Edward Burns": "https://image.tmdb.org/t/p/w185/8Z7Y4E2m1T0X7jY3Q4Y5Z6W7X8Y.jpg",
                "Karen Allen": "https://image.tmdb.org/t/p/w185/8Z7Y4E2m1T0X7jY3Q4Y5Z6W7X8Y.jpg",
                "Paul Freeman": "https://image.tmdb.org/t/p/w185/8Z7Y4E2m1T0X7jY3Q4Y5Z6W7X8Y.jpg",
                "Ronald Lacey": "https://image.tmdb.org/t/p/w185/8Z7Y4E2m1T0X7jY3Q4Y5Z6W7X8Y.jpg",
                "Mark Wahlberg": "https://image.tmdb.org/t/p/w185/8Z7Y4E2m1T0X7jY3Q4Y5Z6W7X8Y.jpg",
                "Alexandre Rodrigues": "https://image.tmdb.org/t/p/w185/8Z7Y4E2m1T0X7jY3Q4Y5Z6W7X8Y.jpg",
                "Leandro Firmino": "https://image.tmdb.org/t/p/w185/8Z7Y4E2m1T0X7jY3Q4Y5Z6W7X8Y.jpg",
                "Phellipe Haagensen": "https://image.tmdb.org/t/p/w185/8Z7Y4E2m1T0X7jY3Q4Y5Z6W7X8Y.jpg",
                "Douglas Silva": "https://image.tmdb.org/t/p/w185/8Z7Y4E2m1T0X7jY3Q4Y5Z6W7X8Y.jpg",
                "Miles Teller": "https://image.tmdb.org/t/p/w185/8u8Z7T3h3l2VgBRHqpWJgKJj4rZ.jpg",
                "Melissa Benoist": "https://image.tmdb.org/t/p/w185/8Z7Y4E2m1T0X7jY3Q4Y5Z6W7X8Y.jpg",
                "Austin Stowell": "https://image.tmdb.org/t/p/w185/8Z7Y4E2m1T0X7jY3Q4Y5Z6W7X8Y.jpg",
                "Guy Pearce": "https://image.tmdb.org/t/p/w185/8Z7Y4E2m1T0X7jY3Q4Y5Z6W7X8Y.jpg",
                "Joe Pantoliano": "https://image.tmdb.org/t/p/w185/8Z7Y4E2m1T0X7jY3Q4Y5Z6W7X8Y.jpg",
                "Mark Boone Junior": "https://image.tmdb.org/t/p/w185/8Z7Y4E2m1T0X7jY3Q4Y5Z6W7X8Y.jpg",
                "Hugh Jackman": "https://image.tmdb.org/t/p/w185/8Z7Y4E2m1T0X7jY3Q4Y5Z6W7X8Y.jpg",
                "Toshio Suzuki": "https://image.tmdb.org/t/p/w185/8Z7Y4E2m1T0X7jY3Q4Y5Z6W7X8Y.jpg",
                # New actors from additional movies
                "Timothée Chalamet": "https://image.tmdb.org/t/p/w185/BE2sdjpgsa2rNTFa66f7upkaOP.jpg",
                "Hugh Grant": "https://image.tmdb.org/t/p/w185/tMefBSflR6PGKSxBfI4gsXyzjlG.jpg",
                "Olivia Colman": "https://image.tmdb.org/t/p/w185/uJNaSTsfF9K3pKF1HwAGH1eqU3G.jpg",
                "Keegan-Michael Key": "https://image.tmdb.org/t/p/w185/vq4hrwiM05c8o2TxaJIspyo0O9Q.jpg",
                "Rowan Atkinson": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "Sally Hawkins": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "Jim Carter": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "Natasha Rothwell": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "Mathew Baynton": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "Simon Farnaby": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "Rich Fulcher": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "Rakhee Thakrar": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "Kobna Holdbrook-Smith": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "Tom Davis": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "Ellie White": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "Freya Parker": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "Calah Lane": "https://image.tmdb.org/t/p/w185/z1PmE1aDTYH7H6jx6FeHh70uw4E.jpg",
                "Matt Lucas": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "Brad Pitt": "https://image.tmdb.org/t/p/w185/oTB9vGIBacH5aQNS0pUM74QSWuf.jpg",
                "Joey King": "https://image.tmdb.org/t/p/w185/b0diEOPPAxOOInWOP9kofjYJ9HH.jpg",
                "Aaron Taylor-Johnson": "https://image.tmdb.org/t/p/w185/7pKHxN3bNicXO0bQEsxG0UmE2M6.jpg",
                "Brian Tyree Henry": "https://image.tmdb.org/t/p/w185/eQ5qNjxv8Q5sTLTwJCMQkfWNdGw.jpg",
                "Benedict Cumberbatch": "https://image.tmdb.org/t/p/w185/fBEucxECxGLKVHBznO0P8k4V4k0.jpg",
                "Kirsten Dunst": "https://image.tmdb.org/t/p/w185/6RAAxI4oPnDMzXpXWgkkzSgnIAJ.jpg",
                "Jesse Plemons": "https://image.tmdb.org/t/p/w185/7InKyjPuQkEzJmUiRh9yozLPpIJ.jpg",
                "Kodi Smit-McPhee": "https://image.tmdb.org/t/p/w185/yZmIxhVz0MHsU6SLMWwS7xZxFMj.jpg",
                "Daniel Craig": "https://image.tmdb.org/t/p/w185/iFerDZUmC5Fu26i4qI8xnUVEHc7.jpg",
                "Ana de Armas": "https://image.tmdb.org/t/p/w185/hHhDVklhnMFc0tZxhxWJxu6MSbR.jpg",
                "Rami Malek": "https://image.tmdb.org/t/p/w185/z9o5RPkZl83lM5nt3NkLmjXfteO.jpg",
                "Léa Seydoux": "https://image.tmdb.org/t/p/w185/bAIvEBxKxKZ62ybbPU75d55cDZy.jpg",
                "Margaret Qualley": "https://image.tmdb.org/t/p/w185/7JXxI3sSDxvKBxOXZzVfKbN4tPr.jpg",
                "Geraldine Viswanathan": "https://image.tmdb.org/t/p/w185/lFz1KLGZAjN18A8KbnFm3v00z5P.jpg",
                "Beanie Feldstein": "https://image.tmdb.org/t/p/w185/7J1eJXwJnADG4m0YCOkfQREYcT5.jpg",
                "Wagner Moura": "https://image.tmdb.org/t/p/w185/6IZ42kqHjKZLHRgT2sUnyInBqBo.jpg",
                "Cailee Spaeny": "https://image.tmdb.org/t/p/w185/qeRCxJGTzP0sFdL5rGBUrWEKdLE.jpg",
                "Dev Patel": "https://image.tmdb.org/t/p/w185/yynA1ZQvH7C5dD9CuyF9ld7ZXXQ.jpg",
                "Sharlto Copley": "https://image.tmdb.org/t/p/w185/lfiWAjKDVhPu8L3qN5wFWXIlMIc.jpg",
                "Pitobash": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "Vipin Sharma": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "Paul Rudd": "https://image.tmdb.org/t/p/w185/8eTtJ7XVXY0BnEeUaSiTAraTIXd.jpg",
                "Carrie Coon": "https://image.tmdb.org/t/p/w185/6f3vMB1qSx9shpiIXMHUaOiUBQN.jpg",
                "Finn Wolfhard": "https://image.tmdb.org/t/p/w185/pYXBp1eJZXpBsdSfLKWcSgPjCXY.jpg",
                "Mckenna Grace": "https://image.tmdb.org/t/p/w185/5EV8GpIv42hDKw29wh14qxzJVVl.jpg",
                "Lily Gladstone": "https://image.tmdb.org/t/p/w185/eAj4BLJWXTqHlhP5L8NuErIZiuj.jpg",
                "Mel Gibson": "https://image.tmdb.org/t/p/w185/jJTyXKRKLPvVDdCoKSV5qRVKy7T.jpg",
                "Sophie Marceau": "https://image.tmdb.org/t/p/w185/9wXL9RCOcj3TH9xJRpfxBXJZZmC.jpg",
                "Patrick McGoohan": "https://image.tmdb.org/t/p/w185/wFTj5tYDTLzMrYQCxZ0quDzMGCv.jpg",
                "Angus Macfadyen": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "Matthew Broderick": "https://image.tmdb.org/t/p/w185/1YsQEKDCz7EvP5fU8r0vH6gf4qf.jpg",
                "Jeremy Irons": "https://image.tmdb.org/t/p/w185/qvbOHhVhCyC9LQILBuQsQsJlVV7.jpg",
                "James Earl Jones": "https://image.tmdb.org/t/p/w185/oqY5JYS9nWRzR0SXUlCCuLFzkVx.jpg",
                "Whoopi Goldberg": "https://image.tmdb.org/t/p/w185/kZYL1c6TDvTxR8pTq1vjZzlA68D.jpg",
                "Arnold Schwarzenegger": "https://image.tmdb.org/t/p/w185/z5lGoKgiphY8aYAfefx3p6xQguQ.jpg",
                "Linda Hamilton": "https://image.tmdb.org/t/p/w185/npqpHyqq60cLvH4kPqU0Hqgn85n.jpg",
                "Edward Furlong": "https://image.tmdb.org/t/p/w185/rkKKUVdL95akPrQiKUXZP1aJ5yC.jpg",
                "Robert Patrick": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "Tom Sizemore": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "Jack Nicholson": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "Gabriel Byrne": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "Benicio del Toro": "https://image.tmdb.org/t/p/w185/qJfAlKXSkR8kDI4PELAnHMCfBqp.jpg",
                "Kevin Pollak": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "Scarlett Johansson": "https://image.tmdb.org/t/p/w185/g6VpfFMpuY5HQivdFYcaXHBXu1L.jpg",
                "Paul Giamatti": "https://image.tmdb.org/t/p/w185/ayEDOXhjB6LAaNkqklsKFLc1Ht3.jpg",
                "Da'Vine Joy Randolph": "https://image.tmdb.org/t/p/w185/hxzObXfiB0EZcp7YKjXqLCpcI2V.jpg",
                "Dominic Sessa": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "Carrie Preston": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "Paul Giamatti": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "Da'Vine Joy Randolph": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "Dominic Sessa": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "Carrie Preston": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "Tate Donovan": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "Brady Hepner": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "Ian Dolley": "https://i.ebayimg.com/images/g/Yc8AAOSwVPNlWX3k/s-l1600.webp",
                "Emma Stone": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "Mark Ruffalo": "https://image.tmdb.org/t/p/w185/zJvcj2lgx4Jd8Dp2pXaNkNQfOuU.jpg",
                "Willem Dafoe": "https://image.tmdb.org/t/p/w185/ui8e4sgZAwMPi3hzEO53jyBJF9B.jpg",
                "Ramy Youssef": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "Jerrod Carmichael": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "Hanna Schygulla": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "Margaret Qualley": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "Christopher Abbott": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "Sandra Hüller": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "Swann Arlaud": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "Milo Machado Graner": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "Antoine Reinartz": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "Samuel Theis": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "Jehnny Beth": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "Saadia Bentaïeb": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "Camille Rutherford": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "Leonardo DiCaprio": "https://image.tmdb.org/t/p/w185/wo2hJpn04vbtmh0B9utCFdsQhxM.jpg",
                "Lily Gladstone": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "Jesse Plemons": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "Tantoo Cardinal": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "John Lithgow": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "Brendan Fraser": "https://image.tmdb.org/t/p/w185/pYiCb6Q2WLBkj7k3XE8dTaZ9PNA.jpg",
                "Cara Jade Myers": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "Janae Collins": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "Jillian Dion": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "Margot Robbie": "https://image.tmdb.org/t/p/w185/euDPyqLnwJszwH1xZDTHgGZHBv.jpg",
                "Ryan Gosling": "https://image.tmdb.org/t/p/w185/lyUyVARQKhGxjF3UXb7tq0H3FzG.jpg",
                "America Ferrera": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "Kate McKinnon": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "Issa Rae": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "Will Ferrell": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "Michael Cera": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "Ariana Greenblatt": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "Alexandra Shipp": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "Hari Nef": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "Sharon Rooney": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "Ana Cruz Kayne": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "Ritu Arya": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "Ncuti Gatwa": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "Scott Evans": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "Jamie Demetriou": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "Connor Swindells": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "Kingsley Ben-Adir": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "Simu Liu": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "John Cena": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "Helen Bauer": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "Nicola Coughlan": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "Emerald Fennell": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "Spike Fearn": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "Rob Brydon": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "Cillian Murphy": "https://image.tmdb.org/t/p/w185/lldeQ91GwIVff43JBrpdbAAeYWj.jpg",
                "Emily Blunt": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "Matt Damon": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "Robert Downey Jr.": "https://image.tmdb.org/t/p/w185/5qHNjhtjMD4YWH3UP0rm4tKwxCL.jpg",
                "Florence Pugh": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "Josh Hartnett": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "Casey Affleck": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "Rami Malek": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "Kenneth Branagh": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "Benny Safdie": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "Jason Clarke": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "Dylan Arnold": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "Tom Conti": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "James D'Arcy": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "David Dencik": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "Matthias Schweighöfer": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "Christopher Denham": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "Michael Angarano": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "Jefferson Hall": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "Jack Quaid": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "Brett Deering": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "Gregory Jbara": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "Louise Lombard": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "Guy Burnet": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "Rory Keane": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "Devon Bostick": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "Josh Zuckerman": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "Olivia Thirlby": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "James Remar": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "Tony Goldwyn": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "Kurt Koehler": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "Macon Blair": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "Trond Fausa": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "Emma Dumont": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "Olli Haaskivi": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "Steven Houska": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "Adam Kroeger": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "Alex Wolff": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "Scott Grimes": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "John Gowans": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "Tim DeKay": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "Pat Skipper": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "Zendaya": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "Rebecca Ferguson": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "Josh Brolin": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "Austin Butler": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "Dave Bautista": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "Christopher Walken": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "Stephen McKinley Henderson": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "Léa Seydoux": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "Souheila Yacoub": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "Tim Blake Nelson": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "Charlotte Rampling": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "Roger Yuan": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "Kaye Dina Rose": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "Joe Walker": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "Tara Lynn Orr": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "Alison Halstead": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "Giusi Merli": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "Molly Mcowan": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "Marisca Mulder": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "Amber Midthunder": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "Anya Taylor-Joy": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "Mike Faist": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "Josh O'Connor": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "Darnell Appling": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "A.J. Lister": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "Hailey Gates": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "Nada Despotovich": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "Jake Jensen": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "Shane T. Lynn": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "Mary Holland": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
                "Geoffrey Grayson": "https://image.tmdb.org/t/p/w185/8qBylBsQf4llkGrWR3qAsOtOU8O.jpg",
            }
            for idx, actor_name in enumerate(movie.cast[:4]):  # Top 4 actors
                cast_entry = Cast(
                    movie_id=movie.id,
                    actor_name=actor_name,
                    character_name=f"Character {idx + 1}",  # Placeholder
                    role="Actor",
                    profile_image_url=cast_profiles.get(actor_name),
                    is_lead=(idx < 2),  # First 2 are leads
                    order=idx
                )
                session.add(cast_entry)
            
            print(f"   ✓ Created movie: {movie.title} with cast")
        
        session.commit()
        print(f"   ✓ Created {len(movies)} movies with cast details")
        
        # Create screenings - Distribute 8-10 movies per cinema
        print("\n📅 Creating screenings with 8-10 movies per cinema...")
        base_date = datetime(2026, 2, 1)  # February 1, 2026
        screening_count = 0
        
        showing_movies = [m for m in movies if m.state == MovieState.SHOWING]
        
        # Distribute movies across cinemas (8-10 movies per cinema)
        import random
        random.seed(42)  # For consistent results
        
        movies_per_cinema = {}
        available_movies = showing_movies.copy()
        
        for cinema in cinemas:
            # Each cinema gets 8-10 movies
            num_movies = random.randint(8, 10)
            if len(available_movies) < num_movies:
                # If running out of movies, recycle from the beginning
                available_movies = showing_movies.copy()
                random.shuffle(available_movies)
            
            cinema_movies = available_movies[:num_movies]
            available_movies = available_movies[num_movies:]
            movies_per_cinema[cinema.id] = cinema_movies
            print(f"   ✓ {cinema.name}: {len(cinema_movies)} movies")
        
        # Create screenings for each cinema's assigned movies
        print(f"\n   Creating screenings for all cinemas...")
        for cinema in cinemas:
            cinema_movies = movies_per_cinema[cinema.id]
            cinema_rooms = [r for r in rooms if r.cinema_id == cinema.id]
            
            # Each movie gets 5 days of screenings
            for day in range(5):  # 5 days: Feb 1-5, 2026
                current_date = base_date + timedelta(days=day)
                
                # Morning, afternoon, evening, night showtimes
                times = [10, 14, 18, 21]
                
                for movie in cinema_movies:
                    for room in cinema_rooms:
                        for time_hour in times:
                            screening_time = current_date.replace(hour=time_hour, minute=0, second=0)
                            
                            # IMAX movies cost more
                            base_price = 20.0 if room.name == "IMAX" else 15.0
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
        print(f"   ✓ Created {screening_count} screenings")
        
        # Create reviews for Parasite and Spirited Away
        parasite = next((m for m in movies if m.title == "Parasite"), None)
        spirited_away = next((m for m in movies if m.title == "Spirited Away"), None)
        
        if parasite:
            reviews_parasite = [
                {"user": users[0], "rating": 5, "title": "Masterpiece", "comment": "Incredible social commentary and suspense."},
                {"user": users[1], "rating": 5, "title": "Brilliant", "comment": "Bong Joon-ho at his best."},
                {"user": users[2], "rating": 4, "title": "Great film", "comment": "Very engaging and thought-provoking."},
            ]
            for rev in reviews_parasite:
                review = Review(
                    user_id=rev["user"].id,
                    movie_id=parasite.id,
                    rating=rev["rating"],
                    title=rev["title"],
                    comment=rev["comment"]
                )
                session.add(review)
        
        if spirited_away:
            reviews_spirited = [
                {"user": users[3], "rating": 5, "title": "Magical", "comment": "Beautiful animation and story."},
                {"user": users[4], "rating": 5, "title": "Classic", "comment": "Hayao Miyazaki's masterpiece."},
                {"user": users[5], "rating": 4, "title": "Wonderful", "comment": "Enchanting and imaginative."},
            ]
            for rev in reviews_spirited:
                review = Review(
                    user_id=rev["user"].id,
                    movie_id=spirited_away.id,
                    rating=rev["rating"],
                    title=rev["title"],
                    comment=rev["comment"]
                )
                session.add(review)
        
        session.commit()
        print(f"   ✓ Created reviews for Parasite and Spirited Away")
        
        # Add additional reviews with likes and dislikes for various movies
        print("\n⭐ Creating additional reviews with likes and dislikes...")
        
        # Helper function to find movie by title
        def find_movie(title):
            return next((m for m in movies if m.title == title), None)
        
        # Reviews for The Power of the Dog
        power_dog = find_movie("The Power of the Dog")
        if power_dog:
            reviews_data = [
                {"user": users[6], "rating": 4, "title": "Slow burn masterpiece", "comment": "Jane Campion delivers a haunting Western with incredible performances.", "likes": 45, "dislikes": 3},
                {"user": users[7], "rating": 3, "title": "Artistic but slow", "comment": "Beautiful cinematography but the pacing is too slow for me.", "likes": 12, "dislikes": 8},
                {"user": users[8], "rating": 5, "title": "Cumberbatch at his best", "comment": "Benedict's performance is chilling and captivating.", "likes": 67, "dislikes": 2},
            ]
            for rev in reviews_data:
                review = Review(
                    user_id=rev["user"].id,
                    movie_id=power_dog.id,
                    rating=rev["rating"],
                    title=rev["title"],
                    comment=rev["comment"],
                    likes=rev["likes"],
                    dislikes=rev["dislikes"]
                )
                session.add(review)
        
        # Reviews for Bullet Train
        bullet_train = find_movie("Bullet Train")
        if bullet_train:
            reviews_data = [
                {"user": users[9], "rating": 4, "title": "Fun action ride", "comment": "Brad Pitt is hilarious, non-stop action and great cast chemistry.", "likes": 89, "dislikes": 5},
                {"user": users[10], "rating": 3, "title": "Entertaining chaos", "comment": "Lots of fun but sometimes too over the top.", "likes": 34, "dislikes": 12},
                {"user": users[11], "rating": 5, "title": "Best action comedy of 2022", "comment": "Stylish, funny, and packed with amazing fight scenes!", "likes": 120, "dislikes": 7},
                {"user": users[12], "rating": 2, "title": "Too messy", "comment": "Too many characters and subplots, lost track of what was happening.", "likes": 8, "dislikes": 45},
            ]
            for rev in reviews_data:
                review = Review(
                    user_id=rev["user"].id,
                    movie_id=bullet_train.id,
                    rating=rev["rating"],
                    title=rev["title"],
                    comment=rev["comment"],
                    likes=rev["likes"],
                    dislikes=rev["dislikes"]
                )
                session.add(review)
        
        # Reviews for No Time to Die
        no_time = find_movie("No Time to Die")
        if no_time:
            reviews_data = [
                {"user": users[13], "rating": 5, "title": "Perfect Bond finale", "comment": "Emotional ending to Daniel Craig's Bond era. A must-watch!", "likes": 156, "dislikes": 12},
                {"user": users[14], "rating": 4, "title": "Epic and emotional", "comment": "Great action sequences and a touching ending.", "likes": 78, "dislikes": 6},
                {"user": users[15], "rating": 3, "title": "Too long", "comment": "Good movie but could have been 30 minutes shorter.", "likes": 23, "dislikes": 34},
            ]
            for rev in reviews_data:
                review = Review(
                    user_id=rev["user"].id,
                    movie_id=no_time.id,
                    rating=rev["rating"],
                    title=rev["title"],
                    comment=rev["comment"],
                    likes=rev["likes"],
                    dislikes=rev["dislikes"]
                )
                session.add(review)
        
        # Reviews for Drive-Away Dolls
        drive_away = find_movie("Drive-Away Dolls")
        if drive_away:
            reviews_data = [
                {"user": users[16], "rating": 3, "title": "Quirky fun", "comment": "Coen brothers style with some laughs but not their best.", "likes": 15, "dislikes": 8},
                {"user": users[17], "rating": 2, "title": "Disappointing", "comment": "Expected more from Ethan Coen.", "likes": 5, "dislikes": 28},
            ]
            for rev in reviews_data:
                review = Review(
                    user_id=rev["user"].id,
                    movie_id=drive_away.id,
                    rating=rev["rating"],
                    title=rev["title"],
                    comment=rev["comment"],
                    likes=rev["likes"],
                    dislikes=rev["dislikes"]
                )
                session.add(review)
        
        # Reviews for Civil War
        civil_war = find_movie("Civil War")
        if civil_war:
            reviews_data = [
                {"user": users[3], "rating": 4, "title": "Intense and gripping", "comment": "Alex Garland creates a tense dystopian thriller that feels too real.", "likes": 92, "dislikes": 11},
                {"user": users[4], "rating": 5, "title": "Masterful direction", "comment": "Kirsten Dunst delivers a powerful performance in this harrowing journey.", "likes": 134, "dislikes": 8},
                {"user": users[5], "rating": 3, "title": "Good but not great", "comment": "Interesting premise but leaves too many questions unanswered.", "likes": 28, "dislikes": 19},
            ]
            for rev in reviews_data:
                review = Review(
                    user_id=rev["user"].id,
                    movie_id=civil_war.id,
                    rating=rev["rating"],
                    title=rev["title"],
                    comment=rev["comment"],
                    likes=rev["likes"],
                    dislikes=rev["dislikes"]
                )
                session.add(review)
        
        # Reviews for Monkey Man
        monkey_man = find_movie("Monkey Man")
        if monkey_man:
            reviews_data = [
                {"user": users[6], "rating": 4, "title": "Dev Patel's brilliant debut", "comment": "Raw, visceral action and a powerful revenge story.", "likes": 73, "dislikes": 4},
                {"user": users[7], "rating": 5, "title": "John Wick meets Slumdog", "comment": "Incredible action choreography and social commentary!", "likes": 98, "dislikes": 3},
                {"user": users[8], "rating": 3, "title": "Brutal but uneven", "comment": "Great action but story drags in the middle.", "likes": 21, "dislikes": 15},
            ]
            for rev in reviews_data:
                review = Review(
                    user_id=rev["user"].id,
                    movie_id=monkey_man.id,
                    rating=rev["rating"],
                    title=rev["title"],
                    comment=rev["comment"],
                    likes=rev["likes"],
                    dislikes=rev["dislikes"]
                )
                session.add(review)
        
        # Reviews for Ghostbusters: Frozen Empire
        ghostbusters = find_movie("Ghostbusters: Frozen Empire")
        if ghostbusters:
            reviews_data = [
                {"user": users[9], "rating": 3, "title": "Nostalgic fun", "comment": "Not as good as the originals but still entertaining for fans.", "likes": 42, "dislikes": 18},
                {"user": users[10], "rating": 2, "title": "Missed opportunity", "comment": "Too many characters, not enough heart.", "likes": 12, "dislikes": 56},
                {"user": users[11], "rating": 4, "title": "Family-friendly fun", "comment": "Kids loved it! Great visual effects.", "likes": 67, "dislikes": 9},
            ]
            for rev in reviews_data:
                review = Review(
                    user_id=rev["user"].id,
                    movie_id=ghostbusters.id,
                    rating=rev["rating"],
                    title=rev["title"],
                    comment=rev["comment"],
                    likes=rev["likes"],
                    dislikes=rev["dislikes"]
                )
                session.add(review)
        
        # Reviews for Terminator 2
        t2 = find_movie("Terminator 2: Judgment Day")
        if t2:
            reviews_data = [
                {"user": users[7], "rating": 5, "title": "Best action film ever", "comment": "Revolutionary effects and non-stop action. I'll be back!", "likes": 267, "dislikes": 5},
                {"user": users[8], "rating": 5, "title": "Groundbreaking", "comment": "Changed action movies forever. The liquid metal T-1000 was incredible.", "likes": 198, "dislikes": 3},
                {"user": users[9], "rating": 4, "title": "Classic Arnold", "comment": "Better than the first one. Perfect sequel.", "likes": 134, "dislikes": 7},
            ]
            for rev in reviews_data:
                review = Review(
                    user_id=rev["user"].id,
                    movie_id=t2.id,
                    rating=rev["rating"],
                    title=rev["title"],
                    comment=rev["comment"],
                    likes=rev["likes"],
                    dislikes=rev["dislikes"]
                )
                session.add(review)
        
        # Reviews for Saving Private Ryan
        spr = find_movie("Saving Private Ryan")
        if spr:
            reviews_data = [
                {"user": users[10], "rating": 5, "title": "War film masterpiece", "comment": "The opening D-Day scene is the most realistic war sequence ever filmed.", "likes": 289, "dislikes": 4},
                {"user": users[11], "rating": 5, "title": "Spielberg's best", "comment": "Powerful, emotional, and brutally honest about war.", "likes": 234, "dislikes": 6},
                {"user": users[12], "rating": 4, "title": "Intense and moving", "comment": "Hard to watch but important. Tom Hanks is brilliant.", "likes": 167, "dislikes": 8},
            ]
            for rev in reviews_data:
                review = Review(
                    user_id=rev["user"].id,
                    movie_id=spr.id,
                    rating=rev["rating"],
                    title=rev["title"],
                    comment=rev["comment"],
                    likes=rev["likes"],
                    dislikes=rev["dislikes"]
                )
                session.add(review)
        
        # Reviews for The Departed
        departed = find_movie("The Departed")
        if departed:
            reviews_data = [
                {"user": users[13], "rating": 5, "title": "Scorsese at his finest", "comment": "Incredible cast, perfect pacing, amazing twists. Best crime thriller!", "likes": 212, "dislikes": 7},
                {"user": users[14], "rating": 5, "title": "Everyone's incredible", "comment": "DiCaprio, Damon, Nicholson all at their best. Unforgettable performances.", "likes": 178, "dislikes": 5},
                {"user": users[15], "rating": 4, "title": "Tense thriller", "comment": "Keeps you on the edge of your seat. That ending though!", "likes": 145, "dislikes": 9},
            ]
            for rev in reviews_data:
                review = Review(
                    user_id=rev["user"].id,
                    movie_id=departed.id,
                    rating=rev["rating"],
                    title=rev["title"],
                    comment=rev["comment"],
                    likes=rev["likes"],
                    dislikes=rev["dislikes"]
                )
                session.add(review)
        
        # Reviews for The Usual Suspects
        suspects = find_movie("The Usual Suspects")
        if suspects:
            reviews_data = [
                {"user": users[16], "rating": 5, "title": "Mind-blowing twist", "comment": "One of the greatest plot twists in cinema history. Kevin Spacey is phenomenal.", "likes": 256, "dislikes": 6},
                {"user": users[17], "rating": 5, "title": "Perfect crime thriller", "comment": "The ending will blow your mind. Need to watch it twice!", "likes": 189, "dislikes": 4},
                {"user": users[3], "rating": 4, "title": "Clever and gripping", "comment": "Great ensemble cast and brilliant storytelling.", "likes": 134, "dislikes": 7},
            ]
            for rev in reviews_data:
                review = Review(
                    user_id=rev["user"].id,
                    movie_id=suspects.id,
                    rating=rev["rating"],
                    title=rev["title"],
                    comment=rev["comment"],
                    likes=rev["likes"],
                    dislikes=rev["dislikes"]
                )
                session.add(review)
        
        # Reviews for The Prestige
        prestige = find_movie("The Prestige")
        if prestige:
            reviews_data = [
                {"user": users[4], "rating": 5, "title": "Nolan's underrated gem", "comment": "Complex, layered, and endlessly rewatchable. Masterful storytelling.", "likes": 198, "dislikes": 8},
                {"user": users[5], "rating": 4, "title": "Magic and mystery", "comment": "Bale and Jackman are both excellent. The rivalry is captivating.", "likes": 112, "dislikes": 11},
                {"user": users[6], "rating": 5, "title": "Mind-bending brilliance", "comment": "Every scene has meaning. Gets better with each viewing!", "likes": 167, "dislikes": 5},
            ]
            for rev in reviews_data:
                review = Review(
                    user_id=rev["user"].id,
                    movie_id=prestige.id,
                    rating=rev["rating"],
                    title=rev["title"],
                    comment=rev["comment"],
                    likes=rev["likes"],
                    dislikes=rev["dislikes"]
                )
                session.add(review)
        
        # Reviews for Wonka
        wonka = find_movie("Wonka")
        if wonka:
            reviews_data = [
                {"user": users[7], "rating": 4, "title": "Delightful musical", "comment": "Timothée Chalamet brings charm and wonder to young Wonka. Great family film!", "likes": 143, "dislikes": 12},
                {"user": users[8], "rating": 3, "title": "Fun but forgettable", "comment": "Nice visuals and songs but doesn't capture the magic of the original.", "likes": 45, "dislikes": 28},
                {"user": users[9], "rating": 5, "title": "Pure imagination", "comment": "Wholesome, funny, and beautifully made. Hugh Grant steals every scene!", "likes": 189, "dislikes": 9},
                {"user": users[10], "rating": 4, "title": "Sweet and charming", "comment": "A delightful origin story with heart. Kids will love it!", "likes": 98, "dislikes": 7},
            ]
            for rev in reviews_data:
                review = Review(
                    user_id=rev["user"].id,
                    movie_id=wonka.id,
                    rating=rev["rating"],
                    title=rev["title"],
                    comment=rev["comment"],
                    likes=rev["likes"],
                    dislikes=rev["dislikes"]
                )
                session.add(review)
        
        session.commit()
        print(f"   ✓ Created additional reviews with likes and dislikes for various movies")
        
        # Create sample FAQs
        print("❓ Creating sample FAQs...")
        faqs = [
            FAQ(
                question="How do I create an account?",
                answer="To create an account, click on the 'Sign Up' button in the top right corner of the homepage. Fill in your details including your full name, email address, and password. Make sure to use a strong password with at least 8 characters."
            ),
            FAQ(
                question="How do I book movie tickets?",
                answer="Browse our movie listings, select your preferred showtime, choose your seats, and complete the payment process. You will receive a confirmation email with your ticket details and QR code."
            ),
            FAQ(
                question="Can I cancel my ticket booking?",
                answer="Yes, you can cancel your ticket booking up to 2 hours before the showtime. Go to your booking history, select the ticket, and click 'Cancel'. Refunds will be processed according to our refund policy."
            ),
            FAQ(
                question="What payment methods do you accept?",
                answer="We accept major credit cards (Visa, MasterCard, American Express), PayPal, and digital wallets. All payments are processed securely through our encrypted payment gateway."
            ),
            FAQ(
                question="How do I get to the cinema?",
                answer="Each cinema location has detailed directions on our website. You can find parking information, public transport options, and walking directions from the cinema's detail page."
            ),
        ]
        for faq in faqs:
            session.add(faq)
        session.commit()
        print(f"   ✓ Created {len(faqs)} FAQs")
        
        print(f"\n📊 Summary:")
        print(f"   - {len(users)} users ({len([u for u in users if u.is_admin])} admin, {len([u for u in users if not u.is_admin])} regular)")
        print(f"   - {len(cinemas)} cinemas across {len(set([c.city for c in cinemas]))} cities")
        print(f"   - {len(rooms)} rooms")
        print(f"   - {total_seats} seats")
        print(f"   - {len(movies)} movies with cast details and image URLs")
        print(f"   - {screening_count} screenings")
        print(f"   - Reviews for Parasite and Spirited Away")
        print(f"   - 1 demo user (email: demo@cinema.com, password: demo123)")


if __name__ == "__main__":
    seed_database()
