"""
Recreate all database tables - USE WITH CAUTION
This will drop and recreate all tables
"""
from sqlalchemy import inspect
from app.database import engine, Base, init_db
from app.models import *

def recreate_tables(drop_existing=False):
    """Recreate all database tables"""
    
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()
    
    print("📋 Current tables:")
    for table in existing_tables:
        print(f"  - {table}")
    
    if drop_existing:
        print("\n⚠️  WARNING: Dropping all existing tables...")
        response = input("Are you sure? This will delete all data! (yes/no): ")
        if response.lower() != "yes":
            print("❌ Operation cancelled")
            return False
        
        try:
            Base.metadata.drop_all(bind=engine)
            print("✅ All tables dropped")
        except Exception as e:
            print(f"❌ Error dropping tables: {e}")
            return False
    
    print("\n🔄 Creating all tables...")
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ All tables created successfully!")
        
        # Verify tables
        inspector = inspect(engine)
        new_tables = inspector.get_table_names()
        print(f"\n📋 Tables created ({len(new_tables)}):")
        for table in sorted(new_tables):
            print(f"  ✓ {table}")
        
        # Initialize default data
        print("\n🔄 Initializing default data...")
        init_db()
        print("✅ Default data initialized!")
        
        return True
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("DATABASE TABLE RECREATION SCRIPT")
    print("=" * 60)
    
    print("\nOptions:")
    print("1. Create missing tables only (safe)")
    print("2. Drop and recreate all tables (DANGEROUS - deletes all data)")
    
    choice = input("\nEnter your choice (1 or 2): ")
    
    if choice == "1":
        success = recreate_tables(drop_existing=False)
    elif choice == "2":
        success = recreate_tables(drop_existing=True)
    else:
        print("❌ Invalid choice")
        success = False
    
    print("\n" + "=" * 60)
    if success:
        print("✅ OPERATION COMPLETE")
    else:
        print("❌ OPERATION FAILED")
    print("=" * 60)
