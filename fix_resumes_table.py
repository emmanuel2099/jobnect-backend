"""
Fix resumes table - Add missing job_seeker_id column
"""
import os
import sys
from sqlalchemy import create_engine, text, inspect

# Get database URL from environment
DATABASE_URL = os.getenv('DATABASE_URL')

if not DATABASE_URL:
    print("❌ DATABASE_URL environment variable not set")
    print("\nFor Render deployment:")
    print("1. Go to Render Dashboard")
    print("2. Click on your PostgreSQL database")
    print("3. Copy the 'Internal Database URL'")
    print("4. Set it as DATABASE_URL environment variable")
    sys.exit(1)

# Fix for Render's postgres:// URL (should be postgresql://)
if DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

print(f"🔗 Connecting to database...")
print(f"   URL: {DATABASE_URL[:50]}...")

try:
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as conn:
        # Check if resumes table exists
        inspector = inspect(engine)
        if 'resumes' not in inspector.get_table_names():
            print("⚠️  Resumes table doesn't exist yet")
            print("   This is normal for a fresh database")
            sys.exit(0)
        
        # Check if job_seeker_id column exists
        columns = [col['name'] for col in inspector.get_columns('resumes')]
        print(f"\n📋 Current columns in resumes table:")
        for col in columns:
            print(f"   - {col}")
        
        if 'job_seeker_id' in columns:
            print(f"\n✅ job_seeker_id column already exists!")
            sys.exit(0)
        
        print(f"\n🔧 Adding job_seeker_id column...")
        
        # Add the missing column
        conn.execute(text("""
            ALTER TABLE resumes 
            ADD COLUMN IF NOT EXISTS job_seeker_id INTEGER;
        """))
        
        # Add foreign key constraint if job_seekers table exists
        if 'job_seekers' in inspector.get_table_names():
            print(f"🔗 Adding foreign key constraint...")
            try:
                conn.execute(text("""
                    ALTER TABLE resumes 
                    ADD CONSTRAINT fk_resumes_job_seeker 
                    FOREIGN KEY (job_seeker_id) 
                    REFERENCES job_seekers(id) 
                    ON DELETE CASCADE;
                """))
                print(f"✅ Foreign key constraint added")
            except Exception as e:
                if 'already exists' in str(e).lower():
                    print(f"✅ Foreign key constraint already exists")
                else:
                    print(f"⚠️  Could not add foreign key: {e}")
        
        conn.commit()
        
        print(f"\n✅ Successfully added job_seeker_id column to resumes table!")
        
        # Verify the change
        columns_after = [col['name'] for col in inspector.get_columns('resumes')]
        print(f"\n📋 Updated columns in resumes table:")
        for col in columns_after:
            print(f"   - {col}")
        
        print(f"\n🎉 Database migration complete!")
        print(f"\n💡 Next steps:")
        print(f"   1. The resumes table now has the job_seeker_id column")
        print(f"   2. Try registering again in the app")
        print(f"   3. Registration should work now!")
        
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
