"""
Add missing columns to database tables
Run this on Render to fix column issues
"""
import os
from sqlalchemy import create_engine, text

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("❌ DATABASE_URL not set")
    exit(1)

print("=" * 70)
print("🔧 ADDING MISSING COLUMNS TO DATABASE")
print("=" * 70)

engine = create_engine(DATABASE_URL)

try:
    with engine.connect() as conn:
        # Fix 1: Add company_user_id to companies table
        print("\n1️⃣ Checking companies.company_user_id...")
        result = conn.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='companies' AND column_name='company_user_id';
        """))
        
        if result.fetchone():
            print("   ✅ company_user_id already exists")
        else:
            print("   Adding company_user_id column...")
            conn.execute(text("""
                ALTER TABLE companies 
                ADD COLUMN company_user_id INTEGER REFERENCES company_users(id) ON DELETE CASCADE;
            """))
            conn.commit()
            print("   ✅ company_user_id added")
        
        # Fix 2: Ensure job_seeker_id columns exist
        print("\n2️⃣ Checking job_applications.job_seeker_id...")
        result = conn.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='job_applications' AND column_name='job_seeker_id';
        """))
        
        if result.fetchone():
            print("   ✅ job_seeker_id already exists")
        else:
            print("   Adding job_seeker_id column...")
            conn.execute(text("""
                ALTER TABLE job_applications 
                ADD COLUMN job_seeker_id INTEGER REFERENCES job_seekers(id) ON DELETE CASCADE;
            """))
            conn.commit()
            print("   ✅ job_seeker_id added")
        
        print("\n" + "=" * 70)
        print("✅ ALL COLUMNS FIXED")
        print("=" * 70)
        
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
