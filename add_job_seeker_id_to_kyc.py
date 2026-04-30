"""
Add job_seeker_id column to kyc table
"""
import sys
from sqlalchemy import create_engine, text, inspect
import os

# Get database URL from environment
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://jobnect_db_user:ftYcP25S34SsTiRqHWLFvggRdVgx4VXP@dpg-d7d0cpq8qa3s73bdai7g-a.oregon-postgres.render.com/jobnect_db')

# Fix for Render's postgres:// URL
if DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

print("=" * 70)
print("🔧 ADD JOB_SEEKER_ID TO KYC TABLE")
print("=" * 70)
print(f"\n🔗 Connecting to database...")

try:
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as conn:
        # Check if kyc table exists
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        if 'kyc' not in tables:
            print("\n⚠️  KYC table doesn't exist yet")
            print("   Table will be created automatically on first run")
            sys.exit(0)
        
        # Check current columns
        columns = [col['name'] for col in inspector.get_columns('kyc')]
        print(f"\n📋 Current columns in 'kyc' table:")
        for i, col in enumerate(columns, 1):
            print(f"   {i}. {col}")
        
        if 'job_seeker_id' in columns:
            print(f"\n✅ Column 'job_seeker_id' already exists!")
            print("   No migration needed.")
            sys.exit(0)
        
        print(f"\n🔧 Adding 'job_seeker_id' column...")
        
        # Add the missing column
        conn.execute(text("""
            ALTER TABLE kyc 
            ADD COLUMN IF NOT EXISTS job_seeker_id INTEGER;
        """))
        conn.commit()
        print(f"✅ Column added successfully")
        
        # Add unique constraint
        print(f"\n🔧 Adding unique constraint...")
        try:
            conn.execute(text("""
                ALTER TABLE kyc 
                ADD CONSTRAINT kyc_job_seeker_id_unique 
                UNIQUE (job_seeker_id);
            """))
            conn.commit()
            print(f"✅ Unique constraint added")
        except Exception as e:
            if 'already exists' in str(e).lower():
                print(f"✅ Unique constraint already exists")
            else:
                print(f"⚠️  Could not add unique constraint: {e}")
        
        # Add foreign key constraint if job_seekers table exists
        if 'job_seekers' in tables:
            print(f"\n🔗 Adding foreign key constraint...")
            try:
                conn.execute(text("""
                    ALTER TABLE kyc 
                    ADD CONSTRAINT fk_kyc_job_seeker 
                    FOREIGN KEY (job_seeker_id) 
                    REFERENCES job_seekers(id) 
                    ON DELETE CASCADE;
                """))
                conn.commit()
                print(f"✅ Foreign key constraint added")
            except Exception as e:
                if 'already exists' in str(e).lower():
                    print(f"✅ Foreign key constraint already exists")
                else:
                    print(f"⚠️  Could not add foreign key: {e}")
        
        # Verify the change
        columns_after = [col['name'] for col in inspector.get_columns('kyc')]
        print(f"\n📋 Updated columns in 'kyc' table:")
        for i, col in enumerate(columns_after, 1):
            marker = "✨ NEW" if col == 'job_seeker_id' else ""
            print(f"   {i}. {col} {marker}")
        
        print(f"\n" + "=" * 70)
        print(f"🎉 MIGRATION COMPLETE!")
        print("=" * 70)
        print(f"\n✅ The kyc table now has the job_seeker_id column")
        print(f"✅ KYC submission should work now")
        
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
