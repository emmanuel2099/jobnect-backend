"""
Fix database issues - recreate tables and verify connection
"""
import sys
from sqlalchemy import create_engine, text, inspect
from app.config import settings
from app.database import Base, SessionLocal, init_db
from app.models import *  # Import all models

def check_connection():
    """Check if database connection works"""
    try:
        engine = create_engine(settings.DATABASE_URL)
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("✅ Database connection successful")
            return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def check_tables():
    """Check if tables exist"""
    try:
        engine = create_engine(settings.DATABASE_URL)
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        print(f"📋 Found {len(tables)} tables: {tables}")
        return tables
    except Exception as e:
        print(f"❌ Error checking tables: {e}")
        return []

def recreate_tables():
    """Drop and recreate all tables"""
    try:
        print("🔄 Recreating database tables...")
        engine = create_engine(settings.DATABASE_URL)
        
        # Drop all tables
        print("🗑️  Dropping existing tables...")
        Base.metadata.drop_all(bind=engine)
        
        # Create all tables
        print("📝 Creating new tables...")
        Base.metadata.create_all(bind=engine)
        
        print("✅ Tables recreated successfully")
        return True
    except Exception as e:
        print(f"❌ Error recreating tables: {e}")
        import traceback
        print(traceback.format_exc())
        return False

def main():
    print("=" * 60)
    print("DATABASE FIX UTILITY")
    print("=" * 60)
    
    # Step 1: Check connection
    print("\n1️⃣  Checking database connection...")
    if not check_connection():
        print("❌ Cannot connect to database. Check your DATABASE_URL in .env")
        sys.exit(1)
    
    # Step 2: Check existing tables
    print("\n2️⃣  Checking existing tables...")
    tables = check_tables()
    
    # Step 3: Recreate tables
    print("\n3️⃣  Recreating tables...")
    if not recreate_tables():
        print("❌ Failed to recreate tables")
        sys.exit(1)
    
    # Step 4: Verify tables were created
    print("\n4️⃣  Verifying tables...")
    new_tables = check_tables()
    if not new_tables:
        print("❌ No tables found after recreation")
        sys.exit(1)
    
    # Step 5: Initialize with default data
    print("\n5️⃣  Initializing default data...")
    try:
        init_db()
        print("✅ Default data initialized")
    except Exception as e:
        print(f"⚠️  Warning: Could not initialize default data: {e}")
    
    print("\n" + "=" * 60)
    print("✅ DATABASE FIX COMPLETE")
    print("=" * 60)
    print("\nYou can now start the server with: python main.py")

if __name__ == "__main__":
    main()
