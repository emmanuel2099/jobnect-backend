"""
Add company_logo column to users table
Run this script to update the database schema
"""
from sqlalchemy import create_engine, text
from app.config import settings

def add_company_logo_column():
    """Add company_logo column to users table"""
    engine = create_engine(settings.DATABASE_URL)
    
    try:
        with engine.connect() as conn:
            # Check if column already exists
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='users' AND column_name='company_logo'
            """))
            
            if result.fetchone() is None:
                print("Adding company_logo column to users table...")
                conn.execute(text("""
                    ALTER TABLE users 
                    ADD COLUMN company_logo TEXT
                """))
                conn.commit()
                print("✅ Successfully added company_logo column")
            else:
                print("ℹ️  company_logo column already exists")
                
    except Exception as e:
        print(f"❌ Error: {e}")
        raise

if __name__ == "__main__":
    add_company_logo_column()
