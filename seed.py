"""
Database seeding script.

Run this to populate the database with sample data for development/testing.
"""
from datetime import datetime, timedelta, date
from sqlmodel import Session, create_engine, select, text

from app.config import settings
from app.database import engine
from app.models import Cinema, Room, Seat, Movie, Screening, User, Cast, MovieState
from app.services.auth import get_password_hash
from sqlmodel import SQLModel



def clear_database(session: Session):
    """Clear all data from the database to avoid duplicates."""
    print("🗑️  Clearing existing data...")
    
    from sqlalchemy import text
    
    # Truncate all tables with CASCADE to handle dependencies
    session.execute(text('TRUNCATE TABLE "user", movie, cinema, room, seat, screening, "cast", ticket, reviews, review_reactions, favorite, search_history, tokenblacklist CASCADE;'))
    
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
            Cinema(name="Mega Cinema Tunis", address="123 Avenue Habib Bourguiba", city="Tunis"),
            Cinema(name="Pathé Palace", address="456 Avenue de la Liberté", city="Tunis"),
            Cinema(name="CinéMadart", address="789 Rue de Marseille", city="Tunis"),
            Cinema(name="Le Colisée", address="321 Boulevard de la République", city="Sfax"),
            Cinema(name="Ciné Jamil", address="654 Avenue Farhat Hached", city="Sousse"),
            Cinema(name="Rialto Cinema", address="987 Rue de la Kasbah", city="Tunis"),
            Cinema(name="Ciné Atlas", address="147 Boulevard 9 Avril", city="Tunis"),
            Cinema(name="Le Palace", address="258 Rue de Rome", city="Monastir"),
            Cinema(name="Ciné Rex", address="369 Avenue de France", city="Bizerte"),
            Cinema(name="Majestic Cinema", address="741 Rue de l'Indépendance", city="Gabès"),
            Cinema(name="Ciné Alhambra", address="852 Boulevard de l'Environnement", city="Ariana"),
            Cinema(name="Le Royal", address="963 Avenue de la Victoire", city="Kairouan"),
            Cinema(name="Ciné Étoile", address="159 Rue de la Révolution", city="Nabeul"),
            Cinema(name="Palais du Cinéma", address="357 Boulevard de la Paix", city="Hammamet"),
            Cinema(name="Ciné Moderne", address="468 Avenue de la Liberté", city="Mahdia")
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
                title="Braveheart",
                description="Scottish warrior William Wallace leads his countrymen in a rebellion to free his homeland from the tyranny of King Edward I of England.",
                duration_minutes=178,
                genre="Historical",
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
                image_url="https://image.tmdb.org/t/p/w500/or1gBugWhfjHp9VUKJZfxbjQfTM.jpg",
                trailer_url="https://www.youtube.com/watch?v=1NJO0jxBtMo",
                awards=["Academy Award for Best Picture", "Academy Award for Best Director"],
                details={"imdb_rating": 8.3, "historical_drama": True}
            ),
            Movie(
                title="The Lion King",
                description="Lion cub and future king Simba searches for his identity and learns about responsibility and courage.",
                duration_minutes=88,
                genre="Animation",
                rating="G",
                cast=["Matthew Broderick", "Jeremy Irons", "James Earl Jones", "Whoopi Goldberg"],
                director="Roger Allers",
                writers=["Irene Mecchi", "Jonathan Roberts", "Linda Woolverton"],
                producers=["Don Hahn"],
                release_date=date(1994, 6, 24),
                country="USA",
                language="English",
                budget=45000000,
                revenue=968511805,
                production_company="Walt Disney Pictures",
                distributor="Walt Disney Pictures",
                image_url="https://image.tmdb.org/t/p/w500/sKCr78MXSLixwmZ8DyJLfBcFcqq.jpg",
                trailer_url="https://www.youtube.com/watch?v=4sj1MT05lAA",
                awards=["Academy Award for Best Original Score", "Golden Globe for Best Motion Picture"],
                details={"imdb_rating": 8.5, "animated": True}
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
                image_url="https://image.tmdb.org/t/p/w500/5M0j0B18abtBI5gi2RhfjjurT3.jpg",
                trailer_url="https://www.youtube.com/watch?v=CRRlbK5w8AE",
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
                image_url="https://image.tmdb.org/t/p/w500/9IWdJMMlqhbEbVJmZM3k8uuE6TJ.jpg",
                trailer_url="https://www.youtube.com/watch?v=oiXdPolca5w",
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
                image_url="https://image.tmdb.org/t/p/w500/1wY4psJ5NVEhCuOYROGsXQ98Ll.jpg",
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
                image_url="https://image.tmdb.org/t/p/w500/nT97ifFY8gkFgkvTQJz98ZfpMsb.jpg",
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
                image_url="https://image.tmdb.org/t/p/w500/tRNlZbgNCXqR2iQa87eM8DO4ZoV.jpg",
                trailer_url="https://www.youtube.com/watch?v=ijXruSzfGEc",
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
            )
        ]
        
        for movie in movies:
            session.add(movie)
        session.commit()
        
        for movie in movies:
            # Create cast entries
            for idx, actor_name in enumerate(movie.cast[:4]):  # Top 4 actors
                cast_entry = Cast(
                    movie_id=movie.id,
                    actor_name=actor_name,
                    character_name=f"Character {idx + 1}",  # Placeholder
                    role="Actor",
                    profile_image_url=None,
                    is_lead=(idx < 2),  # First 2 are leads
                    order=idx
                )
                session.add(cast_entry)
            
            print(f"   ✓ Created movie: {movie.title} with cast")
        
        session.commit()
        print(f"   ✓ Created {len(movies)} movies with cast details")
        
        # Create screenings (next 7 days)
        print("\n📅 Creating screenings...")
        base_date = datetime.now() - timedelta(days=1)  # Yesterday
        screening_count = 0
        
        for day in range(7):  # Next 7 days
            current_date = base_date + timedelta(days=day)

            # Morning, afternoon, evening, night showtimes
            times = [10, 14, 18, 21]
            
            for idx, movie in enumerate(movies[:15]):  # First 15 movies
                room = rooms[idx % len(rooms)]

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
        
        print("\n✅ Database seeding completed successfully!")
        print(f"\n📊 Summary:")
        print(f"   - {len(users)} users ({len([u for u in users if u.is_admin])} admin, {len([u for u in users if not u.is_admin])} regular)")
        print(f"   - {len(cinemas)} cinemas across {len(set([c.city for c in cinemas]))} cities")
        print(f"   - {len(rooms)} rooms")
        print(f"   - {total_seats} seats")
        print(f"   - {len(movies)} movies with cast details and image URLs")
        print(f"   - {screening_count} screenings")
        print(f"   - 1 demo user (email: demo@cinema.com, password: demo123)")


if __name__ == "__main__":
    seed_database()
