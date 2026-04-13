"""
Simple migration to add company_logo column
"""
import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

def migrate():
    """Add company_logo column to users table"""
    print("🔄 Connecting to database...")
    engine = create_engine(DATABASE_URL)
    
    try:
        with engine.connect() as conn:
            # Check if column exists
            print("🔍 Checking if company_logo column exists...")
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='users' AND column_name='company_logo'
            """))
            
            if result.fetchone() is None:
                print("➕ Adding company_logo column...")
                conn.execute(text("ALTER TABLE users ADD COLUMN company_logo TEXT"))
                conn.commit()
                print("✅ Successfully added company_logo column!")
            else:
                print("ℹ️  company_logo column already exists - no migration needed")
                
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        engine.dispose()
        print("✅ Migration complete!")

if __name__ == "__main__":
    migrate()
