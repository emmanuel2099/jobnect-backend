"""
Add job_seeker_id column to job_applications table
This allows the new JobSeeker model to work with applications
"""

from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("❌ DATABASE_URL not found in environment variables")
    exit(1)

print(f"🔗 Connecting to database...")
engine = create_engine(DATABASE_URL)

try:
    with engine.connect() as conn:
        # Check if column exists
        result = conn.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='job_applications' AND column_name='job_seeker_id';
        """))
        
        if result.fetchone():
            print("✅ job_seeker_id column already exists")
        else:
            print("🔄 Adding job_seeker_id column to job_applications table...")
            
            # Add the column
            conn.execute(text("""
                ALTER TABLE job_applications 
                ADD COLUMN job_seeker_id INTEGER REFERENCES job_seekers(id) ON DELETE CASCADE;
            """))
            
            conn.commit()
            print("✅ job_seeker_id column added successfully")
        
        # Verify the column exists
        result = conn.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='job_applications' AND column_name='job_seeker_id';
        """))
        
        if result.fetchone():
            print("✅ Verification successful - job_seeker_id column exists")
        else:
            print("❌ Verification failed - column not found")
            
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
finally:
    engine.dispose()

print("\n✅ Done!")
