"""
Add is_recommended field to jobs table
"""
import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

def migrate():
    """Add is_recommended column to jobs table"""
    print("🔄 Connecting to database...")
    engine = create_engine(DATABASE_URL)
    
    try:
        with engine.connect() as conn:
            # Check if column exists
            print("🔍 Checking if is_recommended column exists...")
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='jobs' AND column_name='is_recommended'
            """))
            
            if result.fetchone() is None:
                print("➕ Adding is_recommended column...")
                conn.execute(text("ALTER TABLE jobs ADD COLUMN is_recommended BOOLEAN DEFAULT FALSE"))
                conn.commit()
                print("✅ Successfully added is_recommended column!")
            else:
                print("ℹ️  is_recommended column already exists - no migration needed")
                
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        engine.dispose()
        print("✅ Migration complete!")

if __name__ == "__main__":
    migrate()
