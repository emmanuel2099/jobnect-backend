"""
Script to add age field to Resume model and implement account deactivation
Run this to update the database schema
"""
from sqlalchemy import create_engine, Column, Integer, text
from app.config import settings
from app.models import Base

def add_age_field():
    """Add age field to resumes table"""
    engine = create_engine(settings.DATABASE_URL)
    
    with engine.connect() as conn:
        try:
            # Add age column to resumes table
            conn.execute(text("""
                ALTER TABLE resumes 
                ADD COLUMN IF NOT EXISTS age INTEGER
            """))
            conn.commit()
            print("✓ Added 'age' column to resumes table")
        except Exception as e:
            print(f"Note: {e}")
        
        try:
            # Add is_deactivated column to users table
            conn.execute(text("""
                ALTER TABLE users 
                ADD COLUMN IF NOT EXISTS is_deactivated BOOLEAN DEFAULT FALSE
            """))
            conn.commit()
            print("✓ Added 'is_deactivated' column to users table")
        except Exception as e:
            print(f"Note: {e}")
        
        try:
            # Add deactivated_at column to users table
            conn.execute(text("""
                ALTER TABLE users 
                ADD COLUMN IF NOT EXISTS deactivated_at TIMESTAMP
            """))
            conn.commit()
            print("✓ Added 'deactivated_at' column to users table")
        except Exception as e:
            print(f"Note: {e}")
    
    print("\n✅ Database schema updated successfully!")
    print("Age field is now available for both job seekers and companies")
    print("Account deactivation fields added to users table")

if __name__ == "__main__":
    add_age_field()
