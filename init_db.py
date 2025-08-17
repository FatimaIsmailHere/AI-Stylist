#!/usr/bin/env python3
"""Initialize the database with tables"""

import os
from database import Base, engine
from models import User, Outfit, ClothingItem, Recommendation, FashionTrend

def init_database():
    """Create all database tables"""
    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("✓ Database tables created successfully")
        
        # Create a default user for demo
        from database import SessionLocal
        db = SessionLocal()
        
        try:
            # Check if default user exists
            existing_user = db.query(User).filter(User.user_id == 1).first()
            if not existing_user:
                default_user = User(
                    user_id=1,
                    username="demo_user",
                    email="demo@example.com"
                )
                db.add(default_user)
                db.commit()
                print("✓ Default demo user created")
            else:
                print("✓ Default demo user already exists")
        finally:
            db.close()
            
    except Exception as e:
        print(f"✗ Error initializing database: {e}")
        raise

if __name__ == "__main__":
    init_database()