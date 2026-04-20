"""
Force initialize database with all tables and sample data
Run this on Render to ensure everything is set up
"""
from sqlalchemy import inspect, text
from app.database import engine, Base, SessionLocal, init_db
from app.models import *
import sys

def force_initialize():
    """Force create all tables and initialize data"""
    
    print("=" * 60)
    print("FORCE DATABASE INITIALIZATION")
    print("=" * 60)
    
    # Step 1: Check current tables
    print("\n1. Checking existing tables...")
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()
    print(f"   Found {len(existing_tables)} tables:")
    for table in sorted(existing_tables):
        print(f"   - {table}")
    
    # Step 2: Create all tables
    print("\n2. Creating all tables...")
    try:
        Base.metadata.create_all(bind=engine)
        print("   ✅ Tables created successfully")
    except Exception as e:
        print(f"   ❌ Error creating tables: {e}")
        return False
    
    # Step 3: Verify tables were created
    print("\n3. Verifying tables...")
    inspector = inspect(engine)
    new_tables = inspector.get_table_names()
    print(f"   Total tables: {len(new_tables)}")
    
    required_tables = [
        'users', 'resumes', 'companies', 'jobs', 'job_applications',
        'bookmarks', 'job_categories', 'cities', 'job_types', 'job_levels'
    ]
    
    missing_tables = [t for t in required_tables if t not in new_tables]
    if missing_tables:
        print(f"   ⚠️  Missing tables: {missing_tables}")
    else:
        print("   ✅ All required tables exist")
    
    # Step 4: Check job_applications table specifically
    if 'job_applications' in new_tables:
        print("\n4. Checking job_applications table...")
        columns = inspector.get_columns('job_applications')
        print("   Columns:")
        for col in columns:
            print(f"   - {col['name']}: {col['type']}")
        print("   ✅ job_applications table is ready")
    else:
        print("\n4. ❌ job_applications table NOT found!")
        return False
    
    # Step 5: Initialize default data
    print("\n5. Initializing default data...")
    try:
        init_db()
        print("   ✅ Default data initialized")
    except Exception as e:
        print(f"   ⚠️  Warning: {e}")
        print("   (This is OK if data already exists)")
    
    # Step 6: Verify data
    print("\n6. Verifying data...")
    db = SessionLocal()
    try:
        job_count = db.query(Job).count()
        company_count = db.query(Company).count()
        category_count = db.query(JobCategory).count()
        
        print(f"   Jobs: {job_count}")
        print(f"   Companies: {company_count}")
        print(f"   Categories: {category_count}")
        
        if job_count == 0:
            print("   ⚠️  No jobs in database - users won't see any listings")
        else:
            print("   ✅ Database has sample data")
    except Exception as e:
        print(f"   ❌ Error checking data: {e}")
    finally:
        db.close()
    
    print("\n" + "=" * 60)
    print("✅ DATABASE INITIALIZATION COMPLETE")
    print("=" * 60)
    print("\nThe backend is ready to accept job applications!")
    return True

if __name__ == "__main__":
    success = force_initialize()
    sys.exit(0 if success else 1)
