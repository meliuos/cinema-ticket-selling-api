"""
Create admin user script.
"""
from sqlmodel import Session, select
from app.database import engine
from app.models import User
from app.services.auth import get_password_hash

def create_admin():
    """Create admin user with specific credentials."""
    print("👑 Creating admin user...")
    
    with Session(engine) as session:
        # Check if admin already exists
        existing_admin = session.exec(
            select(User).where(User.email == "admin@cineway.com")
        ).first()
        
        if existing_admin:
            print(f"⚠️  Admin user already exists: {existing_admin.email}")
            # Update password and admin status
            existing_admin.hashed_password = get_password_hash("AdminCineway@12345")
            existing_admin.is_admin = True
            existing_admin.is_active = True
            session.add(existing_admin)
            session.commit()
            print("   ✓ Updated admin credentials")
        else:
            # Create new admin user
            admin_user = User(
                email="admin@cineway.com",
                full_name="Cinema Admin",
                hashed_password=get_password_hash("AdminCineway@12345"),
                is_active=True,
                is_admin=True
            )
            session.add(admin_user)
            session.commit()
            session.refresh(admin_user)
            print(f"   ✓ Created admin user: {admin_user.email}")
        
        print("\n✅ Admin user ready!")
        print("   Email: admin@cineway.com")
        print("   Password: AdminCineway@12345")

if __name__ == "__main__":
    create_admin()
