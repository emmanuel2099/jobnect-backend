"""
Add tier column to job_categories table
"""
from sqlalchemy import text
from app.database import SessionLocal, engine

def add_tier_column():
    """Add tier column to job_categories table"""
    db = SessionLocal()
    
    try:
        print("=" * 60)
        print("🔧 ADDING TIER COLUMN TO JOB_CATEGORIES")
        print("=" * 60)
        
        # Check if tier column exists
        result = db.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='job_categories' AND column_name='tier';
        """))
        
        if result.fetchone():
            print("✅ Tier column already exists")
        else:
            print("📝 Adding tier column...")
            db.execute(text("""
                ALTER TABLE job_categories 
                ADD COLUMN tier VARCHAR(10) DEFAULT 'low';
            """))
            db.commit()
            print("✅ Tier column added successfully")
        
        print("\n" + "=" * 60)
        print("✅ DONE!")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    add_tier_column()
