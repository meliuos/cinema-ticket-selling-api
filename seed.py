"""
Database seeding script.

Run this to populate the database with sample data for development/testing.
"""
from datetime import datetime, timedelta, date
from sqlmodel import Session, create_engine, select, text

from app.config import settings
from app.database import engine
from app.models import Cinema, Room, Seat, Movie, Screening, User
from app.models.review import Review
from app.models.favorite import Favorite
from app.models.search_history import SearchHistory
from app.models.cast import Cast
from app.models.ticket import Ticket
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
        
        # Create sample users
        print("👤 Creating sample users...")
        users = [
            User(
                email="admin@cinema.com",
                full_name="Admin User",
                hashed_password=get_password_hash("admin123"),
                is_active=True,
                is_admin=True,
                date_of_birth=datetime(1985, 3, 20),
                dark_mode=True,
                notifications_enabled=True,
                newsletter_subscribed=False
            ),
            User(
                email="demo@cinema.com",
                full_name="Demo User",
                hashed_password=get_password_hash("demo123"),
                is_active=True,
                is_admin=False,
                date_of_birth=datetime(1990, 1, 15),
                dark_mode=False,
                notifications_enabled=True,
                newsletter_subscribed=True
            ),
            User(
                email="john.doe@example.com",
                full_name="John Doe",
                hashed_password=get_password_hash("password123"),
                is_active=True,
                is_admin=False,
                date_of_birth=datetime(1995, 7, 8),
                dark_mode=False,
                notifications_enabled=True,
                newsletter_subscribed=True
            ),
            User(
                email="jane.smith@example.com",
                full_name="Jane Smith",
                hashed_password=get_password_hash("password123"),
                is_active=True,
                is_admin=False,
                date_of_birth=datetime(1988, 11, 22),
                dark_mode=True,
                notifications_enabled=False,
                newsletter_subscribed=False
            )
        ]

        for user in users:
            session.add(user)
        session.commit()

        for user in users:
            session.refresh(user)
            print(f"   ✓ Created user: {user.email} (Admin: {user.is_admin})")
        
        # Create cinemas
        print("\n🎬 Creating cinemas...")
        cinemas = [
            Cinema(
                name="Mega Cinema Tunis",
                address="123 Avenue Habib Bourguiba",
                city="Tunis",
                longitude=10.1815,
                latitude=36.8065,
                imageurl="https://images.unsplash.com/photo-1489599849927-2ee91cede3ba",
                phone="+216 71 123 456",
                hasParking=True,
                isAccessible=True,
                amenities=["3D", "IMAX", "Dolby Atmos", "Parking", "Restaurant", "VIP Lounge"]
            ),
            Cinema(
                name="Pathé Palace",
                address="456 Avenue de la Liberté",
                city="Tunis",
                longitude=10.1658,
                latitude=36.8189,
                imageurl="https://images.unsplash.com/photo-1478720568477-152d9b164e26",
                phone="+216 71 789 012",
                hasParking=True,
                isAccessible=False,
                amenities=["3D", "Dolby Atmos", "Snack Bar", "Online Booking"]
            ),
            Cinema(
                name="Ciné Carthage",
                address="789 Avenue de Carthage",
                city="Tunis",
                longitude=10.1975,
                latitude=36.8520,
                imageurl="https://images.unsplash.com/photo-1594909122845-11baa439b7bf",
                phone="+216 71 345 678",
                hasParking=False,
                isAccessible=True,
                amenities=["3D", "Premium Seats", "Snack Bar"]
            ),
            Cinema(
                name="Galaxy Cinema Sousse",
                address="22 Boulevard 14 Janvier",
                city="Sousse",
                longitude=10.6408,
                latitude=35.8256,
                imageurl="https://images.unsplash.com/photo-1536440136628-849c177e76a1",
                phone="+216 73 456 789",
                hasParking=True,
                isAccessible=True,
                amenities=["3D", "4DX", "Dolby Atmos", "Parking", "Restaurant"]
            ),
            Cinema(
                name="Cinépolis Sfax",
                address="88 Avenue Majida Boulila",
                city="Sfax",
                longitude=10.7602,
                latitude=34.7406,
                imageurl="https://images.unsplash.com/photo-1598899134739-24c46f58b8c0",
                phone="+216 74 567 890",
                hasParking=True,
                isAccessible=False,
                amenities=["3D", "IMAX", "Luxury Recliners", "Parking"]
            )
        ]
        
        for cinema in cinemas:
            session.add(cinema)
        session.commit()
        
        for cinema in cinemas:
            session.refresh(cinema)
            print(f"   ✓ Created cinema: {cinema.name}")
        
        # Create rooms for all cinemas
        print("\n🚪 Creating rooms...")
        rooms = [
            # Mega Cinema Tunis - 3 rooms
            Room(name="Room 1", cinema_id=cinemas[0].id),
            Room(name="Room 2", cinema_id=cinemas[0].id),
            Room(name="IMAX Hall", cinema_id=cinemas[0].id),
            # Pathé Palace - 2 rooms
            Room(name="Hall A", cinema_id=cinemas[1].id),
            Room(name="Hall B", cinema_id=cinemas[1].id),
            # Ciné Carthage - 2 rooms
            Room(name="Salle 1", cinema_id=cinemas[2].id),
            Room(name="Salle 2", cinema_id=cinemas[2].id),
            # Galaxy Cinema Sousse - 3 rooms
            Room(name="Screen 1", cinema_id=cinemas[3].id),
            Room(name="Screen 2", cinema_id=cinemas[3].id),
            Room(name="4DX Screen", cinema_id=cinemas[3].id),
            # Cinépolis Sfax - 2 rooms
            Room(name="Premium 1", cinema_id=cinemas[4].id),
            Room(name="IMAX Sfax", cinema_id=cinemas[4].id),
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
            # IMAX and 4DX: 12 rows x 20 seats, Premium: 10 rows x 16 seats, Standard: 8 rows x 12 seats
            if "IMAX" in room.name or "4DX" in room.name:
                rows = 12
                seats_per_row = 20
            elif "Premium" in room.name:
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
            ),
            Movie(
                title="Parasite",
                description="Greed and class discrimination threaten the newly formed symbiotic relationship between the wealthy Park family and the destitute Kim clan.",
                duration_minutes=132,
                genre="Thriller",
                rating="R",
                cast=["Song Kang-ho", "Lee Sun-kyun", "Cho Yeo-jeong", "Choi Woo-shik", "Park So-dam"],
                director="Bong Joon-ho",
                writers=["Bong Joon-ho", "Han Jin-won"],
                producers=["Kwak Sin-ae", "Moon Yang-kwon"],
                release_date=date(2019, 5, 30),
                country="South Korea",
                language="Korean",
                budget=11400000,
                revenue=258800000,
                production_company="CJ Entertainment",
                distributor="CJ Entertainment",
                image_url="https://image.tmdb.org/t/p/w500/7IiTTgloJzvGI1TAYymCfbfl3vT.jpg",
                trailer_url="https://www.youtube.com/watch?v=5xH0HfJHsaY",
                awards=["Academy Award for Best Picture", "Academy Award for Best Director", "Palme d'Or"],
                details={"imdb_rating": 8.5, "first_korean_best_picture": True}
            ),
            Movie(
                title="Avengers: Endgame",
                description="After the devastating events of Infinity War, the Avengers assemble once more to reverse Thanos' actions and restore balance to the universe.",
                duration_minutes=181,
                genre="Action",
                rating="PG-13",
                cast=["Robert Downey Jr.", "Chris Evans", "Mark Ruffalo", "Chris Hemsworth", "Scarlett Johansson"],
                director="Anthony Russo, Joe Russo",
                writers=["Christopher Markus", "Stephen McFeely"],
                producers=["Kevin Feige"],
                release_date=date(2019, 4, 26),
                country="USA",
                language="English",
                budget=356000000,
                revenue=2797800564,
                production_company="Marvel Studios",
                distributor="Walt Disney Studios",
                image_url="https://image.tmdb.org/t/p/w500/or06FN3Dka5tukK1e9sl16pB3iy.jpg",
                trailer_url="https://www.youtube.com/watch?v=TcMBFSGVi1c",
                awards=["Nominated for Best Visual Effects"],
                details={"imdb_rating": 8.4, "mcu_phase": 3, "highest_grossing_film": True}
            ),
            Movie(
                title="Joker",
                description="In Gotham City, mentally troubled comedian Arthur Fleck is disregarded and mistreated by society. He then embarks on a downward spiral of revolution and bloody crime.",
                duration_minutes=122,
                genre="Drama",
                rating="R",
                cast=["Joaquin Phoenix", "Robert De Niro", "Zazie Beetz", "Frances Conroy"],
                director="Todd Phillips",
                writers=["Todd Phillips", "Scott Silver"],
                producers=["Todd Phillips", "Bradley Cooper", "Emma Tillinger Koskoff"],
                release_date=date(2019, 10, 4),
                country="USA",
                language="English",
                budget=55000000,
                revenue=1074251311,
                production_company="Warner Bros. Pictures",
                distributor="Warner Bros. Pictures",
                image_url="https://image.tmdb.org/t/p/w500/udDclJoHjfjb8Ekgsd4FDteOkCU.jpg",
                trailer_url="https://www.youtube.com/watch?v=zAGVQLHvwOY",
                awards=["Academy Award for Best Actor (Joaquin Phoenix)", "Golden Lion at Venice"],
                details={"imdb_rating": 8.4, "controversial": True}
            ),
            Movie(
                title="Dune",
                description="A noble family becomes embroiled in a war for control over the galaxy's most valuable asset while its heir becomes troubled by visions of a dark future.",
                duration_minutes=155,
                genre="Sci-Fi",
                rating="PG-13",
                cast=["Timothée Chalamet", "Rebecca Ferguson", "Oscar Isaac", "Josh Brolin", "Zendaya"],
                director="Denis Villeneuve",
                writers=["Jon Spaihts", "Denis Villeneuve", "Eric Roth"],
                producers=["Mary Parent", "Cale Boyter", "Denis Villeneuve"],
                release_date=date(2021, 10, 22),
                country="USA",
                language="English",
                budget=165000000,
                revenue=400700000,
                production_company="Legendary Pictures",
                distributor="Warner Bros. Pictures",
                image_url="https://image.tmdb.org/t/p/w500/d5NXSklXo0qyIYkgV94XAgMIckC.jpg",
                trailer_url="https://www.youtube.com/watch?v=8g18jFHCLXk",
                awards=["Academy Award for Best Cinematography", "Academy Award for Best Original Score"],
                details={"imdb_rating": 8.0, "based_on_novel": True}
            ),
            Movie(
                title="Spider-Man: No Way Home",
                description="With Spider-Man's identity now revealed, Peter asks Doctor Strange for help. When a spell goes wrong, dangerous foes from other worlds start to appear.",
                duration_minutes=148,
                genre="Action",
                rating="PG-13",
                cast=["Tom Holland", "Zendaya", "Benedict Cumberbatch", "Jacob Batalon"],
                director="Jon Watts",
                writers=["Chris McKenna", "Erik Sommers"],
                producers=["Kevin Feige", "Amy Pascal"],
                release_date=date(2021, 12, 17),
                country="USA",
                language="English",
                budget=200000000,
                revenue=1916000000,
                production_company="Marvel Studios",
                distributor="Sony Pictures",
                image_url="https://image.tmdb.org/t/p/w500/1g0dhYtq4irTY1GPXvft6k4YLjm.jpg",
                trailer_url="https://www.youtube.com/watch?v=JfVOs4VSpmA",
                awards=["Nominated for Best Visual Effects"],
                details={"imdb_rating": 8.2, "mcu_phase": 4, "multiverse": True}
            ),
            Movie(
                title="The Shawshank Redemption",
                description="Two imprisoned men bond over a number of years, finding solace and eventual redemption through acts of common decency.",
                duration_minutes=142,
                genre="Drama",
                rating="R",
                cast=["Tim Robbins", "Morgan Freeman", "Bob Gunton", "William Sadler"],
                director="Frank Darabont",
                writers=["Frank Darabont", "Stephen King"],
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
                awards=["Nominated for 7 Academy Awards"],
                details={"imdb_rating": 9.3, "based_on_stephen_king": True}
            ),
            Movie(
                title="Forrest Gump",
                description="The presidencies of Kennedy and Johnson, the Vietnam War, and other historical events unfold from the perspective of an Alabama man with an IQ of 75.",
                duration_minutes=142,
                genre="Drama",
                rating="PG-13",
                cast=["Tom Hanks", "Robin Wright", "Gary Sinise", "Sally Field"],
                director="Robert Zemeckis",
                writers=["Eric Roth"],
                producers=["Wendy Finerman", "Steve Tisch", "Steve Starkey"],
                release_date=date(1994, 7, 6),
                country="USA",
                language="English",
                budget=55000000,
                revenue=678200000,
                production_company="Paramount Pictures",
                distributor="Paramount Pictures",
                image_url="https://image.tmdb.org/t/p/w500/saHP97rTPS5eLmrLQEcANmKrsFl.jpg",
                trailer_url="https://www.youtube.com/watch?v=bLvqoHBptjg",
                awards=["Academy Award for Best Picture", "Academy Award for Best Actor (Tom Hanks)"],
                details={"imdb_rating": 8.8, "iconic_quotes": True}
            ),
            Movie(
                title="Gladiator",
                description="A former Roman General sets out to exact vengeance against the corrupt emperor who murdered his family and sent him into slavery.",
                duration_minutes=155,
                genre="Action",
                rating="R",
                cast=["Russell Crowe", "Joaquin Phoenix", "Connie Nielsen", "Oliver Reed"],
                director="Ridley Scott",
                writers=["David Franzoni", "John Logan", "William Nicholson"],
                producers=["Douglas Wick", "David Franzoni", "Branko Lustig"],
                release_date=date(2000, 5, 5),
                country="USA",
                language="English",
                budget=103000000,
                revenue=460583960,
                production_company="DreamWorks Pictures",
                distributor="Universal Pictures",
                image_url="https://image.tmdb.org/t/p/w500/ty8TGRuvJLPUmAR1H1nRIsgwvim.jpg",
                trailer_url="https://www.youtube.com/watch?v=owK1qxDselE",
                awards=["Academy Award for Best Picture", "Academy Award for Best Actor (Russell Crowe)"],
                details={"imdb_rating": 8.5, "historical_epic": True}
            ),
            Movie(
                title="The Lion King",
                description="Lion prince Simba and his father are targeted by his bitter uncle, who wants to ascend the throne himself.",
                duration_minutes=88,
                genre="Animation",
                rating="G",
                cast=["Matthew Broderick", "James Earl Jones", "Jeremy Irons", "Moira Kelly"],
                director="Roger Allers, Rob Minkoff",
                writers=["Irene Mecchi", "Jonathan Roberts", "Linda Woolverton"],
                producers=["Don Hahn"],
                release_date=date(1994, 6, 24),
                country="USA",
                language="English",
                budget=45000000,
                revenue=968500000,
                production_company="Walt Disney Pictures",
                distributor="Buena Vista Pictures",
                image_url="https://image.tmdb.org/t/p/w500/sKCr78MXSLixwmZ8DyJLrpMsd15.jpg",
                trailer_url="https://www.youtube.com/watch?v=4CbLXeGSDxg",
                awards=["Academy Award for Best Original Score", "Academy Award for Best Original Song"],
                details={"imdb_rating": 8.5, "disney_renaissance": True}
            ),
            Movie(
                title="Oppenheimer",
                description="The story of American scientist J. Robert Oppenheimer and his role in the development of the atomic bomb.",
                duration_minutes=180,
                genre="Biography",
                rating="R",
                cast=["Cillian Murphy", "Emily Blunt", "Matt Damon", "Robert Downey Jr.", "Florence Pugh"],
                director="Christopher Nolan",
                writers=["Christopher Nolan"],
                producers=["Emma Thomas", "Christopher Nolan", "Charles Roven"],
                release_date=date(2023, 7, 21),
                country="USA",
                language="English",
                budget=100000000,
                revenue=952000000,
                production_company="Universal Pictures",
                distributor="Universal Pictures",
                image_url="https://image.tmdb.org/t/p/w500/8Gxv8gSFCU0XGDykEGv7zR1n2ua.jpg",
                trailer_url="https://www.youtube.com/watch?v=uYPbbksJxIg",
                awards=["Academy Award for Best Picture", "Academy Award for Best Director", "Academy Award for Best Actor"],
                details={"imdb_rating": 8.3, "biographical": True, "imax_filmed": True}
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
        all_screenings = []

        for day in range(7):  # Next 7 days
            current_date = base_date + timedelta(days=day)

            # Morning, afternoon, evening, night showtimes
            times = [10, 14, 18, 21]

            # Rotate through movies and rooms
            for idx, movie in enumerate(movies[:10]):  # Use first 10 movies
                room = rooms[idx % len(rooms)]

                for time_hour in times:
                    screening_time = current_date.replace(hour=time_hour, minute=0, second=0)

                    # IMAX/Premium rooms cost more
                    if "IMAX" in room.name or "Premium" in room.name:
                        base_price = 20.0
                    elif "4DX" in room.name:
                        base_price = 25.0
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
                    all_screenings.append(screening)
                    screening_count += 1

        session.commit()

        # Refresh all screenings to get their IDs
        for screening in all_screenings:
            session.refresh(screening)

        print(f"   ✓ Created {screening_count} screenings")

        # Create cast members for movies
        print("\n🎭 Creating cast members...")
        cast_members = [
            # The Matrix
            Cast(name="Keanu Reeves", movie_id=movies[0].id, actor_name="Keanu Reeves", role="Neo", is_lead=True, order=1, profile_image_url="https://image.tmdb.org/t/p/w500/rRdru6REr9i3WIHv2mntpcgxnoY.jpg"),
            Cast(name="Laurence Fishburne", movie_id=movies[0].id, actor_name="Laurence Fishburne", role="Morpheus", is_lead=True, order=2, profile_image_url="https://image.tmdb.org/t/p/w500/8suOhUmPbfKqDQ17bR0Vst35nk4.jpg"),
            Cast(name="Carrie-Anne Moss", movie_id=movies[0].id, actor_name="Carrie-Anne Moss", role="Trinity", is_lead=True, order=3, profile_image_url="https://image.tmdb.org/t/p/w500/xD4jTA3KmVp5Rq3aHcymL9DUGjD.jpg"),
            # Inception
            Cast(name="Leonardo DiCaprio", movie_id=movies[1].id, actor_name="Leonardo DiCaprio", role="Dom Cobb", is_lead=True, order=1, profile_image_url="https://image.tmdb.org/t/p/w500/wo2hJpn04vbtmh0B9utCFdsQhxM.jpg"),
            Cast(name="Joseph Gordon-Levitt", movie_id=movies[1].id, actor_name="Joseph Gordon-Levitt", role="Arthur", is_lead=False, order=2, profile_image_url="https://image.tmdb.org/t/p/w500/z2FA8js799xqtfiFjBTicFYdfk.jpg"),
            # The Dark Knight
            Cast(name="Christian Bale", movie_id=movies[2].id, actor_name="Christian Bale", role="Bruce Wayne / Batman", is_lead=True, order=1, profile_image_url="https://image.tmdb.org/t/p/w500/vecCvACI30scbblvQ8LDOuSBu87.jpg"),
            Cast(name="Heath Ledger", movie_id=movies[2].id, actor_name="Heath Ledger", role="Joker", is_lead=True, order=2, profile_image_url="https://image.tmdb.org/t/p/w500/5Y9HnYYa9jF4NunY9lSgJGjSe8E.jpg"),
            # Oppenheimer
            Cast(name="Cillian Murphy", movie_id=movies[10].id, actor_name="Cillian Murphy", role="J. Robert Oppenheimer", is_lead=True, order=1, profile_image_url="https://image.tmdb.org/t/p/w500/dm6V24NjjvjMiCtbMkc8Y2WPm2e.jpg"),
            Cast(name="Emily Blunt", movie_id=movies[10].id, actor_name="Emily Blunt", role="Kitty Oppenheimer", is_lead=False, order=2, profile_image_url="https://image.tmdb.org/t/p/w500/5nCSG5TL1bP1geD8aaBfaRzbH1k.jpg"),
        ]

        for cast in cast_members:
            session.add(cast)
        session.commit()
        print(f"   ✓ Created {len(cast_members)} cast members")

        # Create reviews
        print("\n⭐ Creating reviews...")
        reviews = [
            Review(user_id=users[1].id, movie_id=movies[0].id, rating=5, title="Mind-blowing!", comment="The Matrix changed cinema forever. A masterpiece of sci-fi.", likes=42, dislikes=2),
            Review(user_id=users[2].id, movie_id=movies[0].id, rating=4, title="Great action", comment="Loved the action sequences and the concept.", likes=28, dislikes=1),
            Review(user_id=users[3].id, movie_id=movies[1].id, rating=5, title="Nolan's best work", comment="Inception is a complex and brilliant film. The ending is perfect.", likes=95, dislikes=3),
            Review(user_id=users[1].id, movie_id=movies[2].id, rating=5, title="Heath Ledger was incredible", comment="The Dark Knight is the best superhero movie ever made.", likes=156, dislikes=5),
            Review(user_id=users[2].id, movie_id=movies[2].id, rating=5, title="Perfect Batman film", comment="Everything about this movie is perfect.", likes=89, dislikes=2),
            Review(user_id=users[3].id, movie_id=movies[3].id, rating=4, title="Visually stunning", comment="Interstellar is a beautiful and emotional journey through space.", likes=67, dislikes=4),
            Review(user_id=users[1].id, movie_id=movies[5].id, rating=5, title="Absolutely brilliant", comment="Parasite is a masterclass in filmmaking. Deserved all the awards.", likes=103, dislikes=1),
            Review(user_id=users[2].id, movie_id=movies[6].id, rating=5, title="Epic conclusion", comment="Endgame was everything I hoped for and more.", likes=134, dislikes=8),
            Review(user_id=users[3].id, movie_id=movies[7].id, rating=5, title="Joaquin Phoenix is phenomenal", comment="This movie is dark and powerful. Phoenix's performance is unforgettable.", likes=98, dislikes=12),
            Review(user_id=users[1].id, movie_id=movies[10].id, rating=5, title="Nolan does it again", comment="Oppenheimer is a historical epic that everyone should see.", likes=76, dislikes=3),
        ]

        for review in reviews:
            session.add(review)
        session.commit()
        print(f"   ✓ Created {len(reviews)} reviews")

        # Create favorites
        print("\n❤️ Creating favorites...")
        favorites = [
            Favorite(user_id=users[1].id, cinema_id=cinemas[0].id),
            Favorite(user_id=users[1].id, cinema_id=cinemas[3].id),
            Favorite(user_id=users[2].id, cinema_id=cinemas[1].id),
            Favorite(user_id=users[2].id, cinema_id=cinemas[4].id),
            Favorite(user_id=users[3].id, cinema_id=cinemas[0].id),
            Favorite(user_id=users[3].id, cinema_id=cinemas[2].id),
        ]

        for favorite in favorites:
            session.add(favorite)
        session.commit()
        print(f"   ✓ Created {len(favorites)} favorites")

        # Create search history
        print("\n🔍 Creating search history...")
        search_history = [
            SearchHistory(user_id=users[1].id, search_query="action movies", search_type="movie"),
            SearchHistory(user_id=users[1].id, search_query="Nolan", search_type="director"),
            SearchHistory(user_id=users[1].id, search_query="Tunis cinemas", search_type="cinema"),
            SearchHistory(user_id=users[2].id, search_query="sci-fi", search_type="genre"),
            SearchHistory(user_id=users[2].id, search_query="IMAX", search_type="cinema"),
            SearchHistory(user_id=users[3].id, search_query="The Dark Knight", search_type="movie"),
            SearchHistory(user_id=users[3].id, search_query="Christopher Nolan", search_type="director"),
        ]

        for search in search_history:
            session.add(search)
        session.commit()
        print(f"   ✓ Created {len(search_history)} search history entries")

        # Create sample tickets
        print("\n🎫 Creating sample tickets...")
        tickets = [
            Ticket(user_id=users[1].id, screening_id=all_screenings[0].id, seat_id=1, price=all_screenings[0].price, status="confirmed", confirmed_at=datetime.now() - timedelta(days=2)),
            Ticket(user_id=users[1].id, screening_id=all_screenings[5].id, seat_id=25, price=all_screenings[5].price, status="confirmed", confirmed_at=datetime.now() - timedelta(days=1)),
            Ticket(user_id=users[2].id, screening_id=all_screenings[1].id, seat_id=50, price=all_screenings[1].price, status="pending"),
            Ticket(user_id=users[2].id, screening_id=all_screenings[2].id, seat_id=75, price=all_screenings[2].price, status="confirmed", confirmed_at=datetime.now() - timedelta(hours=5)),
            Ticket(user_id=users[3].id, screening_id=all_screenings[10].id, seat_id=100, price=all_screenings[10].price, status="confirmed", confirmed_at=datetime.now() - timedelta(hours=12)),
        ]

        for ticket in tickets:
            session.add(ticket)
        session.commit()
        print(f"   ✓ Created {len(tickets)} tickets")

        print("\n✅ Database seeding completed successfully!")
        print(f"\n📊 Summary:")
        print(f"   - {len(users)} users (1 admin, {len(users)-1} regular)")
        print(f"   - {len(cinemas)} cinemas across {len(set([c.city for c in cinemas]))} cities")
        print(f"   - {len(rooms)} rooms")
        print(f"   - {total_seats} seats")
        print(f"   - {len(movies)} movies (with enhanced details)")
        print(f"   - {screening_count} screenings")
        print(f"   - {len(cast_members)} cast members")
        print(f"   - {len(reviews)} reviews")
        print(f"   - {len(favorites)} favorites")
        print(f"   - {len(search_history)} search history entries")
        print(f"   - {len(tickets)} tickets")
        print(f"\n🔑 Login Credentials:")
        print(f"   - Admin: admin@cinema.com / admin123")
        print(f"   - Demo User: demo@cinema.com / demo123")
        print(f"   - User 1: john.doe@example.com / password123")
        print(f"   - User 2: jane.smith@example.com / password123")


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
