"""Fix movie cast data - convert strings to dictionaries"""
from sqlmodel import Session
from app.database import engine
from app.models import Movie

with Session(engine) as session:
    # Get all movies
    movies = session.query(Movie).all()
    count = 0
    
    for movie in movies:
        if movie.cast:
            # Convert string cast to dict format
            movie.cast = [{"name": actor, "character": ""} for actor in movie.cast]
            count += 1
    
    session.commit()
    print(f"✓ Updated {count} movies with cast data")
