"""
Script to create a test user in the database
"""
from sqlmodel import Session, select
from app.database import engine
from app.models import User
from app.utils.security import get_password_hash

def create_test_user():
    """Create a test user with the specified credentials"""
    test_email = "chabbahamin5@gmail.com"
    test_password = "123456789"
    
    with Session(engine) as session:
        # Check if user already exists
        statement = select(User).where(User.email == test_email)
        existing_user = session.exec(statement).first()
        
        if existing_user:
            print(f"✅ User {test_email} already exists!")
            print(f"   ID: {existing_user.id}")
            print(f"   Email: {existing_user.email}")
            return
        
        # Create new user
        hashed_password = get_password_hash(test_password)
        new_user = User(
            email=test_email,
            hashed_password=hashed_password,
            full_name="Test User",
            is_active=True,
            is_admin=False
        )
        
        session.add(new_user)
        session.commit()
        session.refresh(new_user)
        
        print(f"✅ Successfully created test user!")
        print(f"   Email: {test_email}")
        print(f"   Password: {test_password}")
        print(f"   ID: {new_user.id}")

if __name__ == "__main__":
    create_test_user()
