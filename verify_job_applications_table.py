"""
Verify and create job_applications table if missing
"""
from sqlalchemy import inspect
from app.database import engine, Base, SessionLocal
from app.models import JobApplication

def verify_and_create_table():
    """Check if job_applications table exists and create if missing"""
    
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()
    
    print("📋 Existing tables:")
    for table in existing_tables:
        print(f"  ✓ {table}")
    
    if "job_applications" not in existing_tables:
        print("\n⚠️  job_applications table is missing!")
        print("🔄 Creating job_applications table...")
        
        try:
            # Create only the job_applications table
            JobApplication.__table__.create(bind=engine, checkfirst=True)
            print("✅ job_applications table created successfully!")
        except Exception as e:
            print(f"❌ Error creating table: {e}")
            return False
    else:
        print("\n✅ job_applications table exists!")
        
        # Check columns
        columns = inspector.get_columns("job_applications")
        print("\n📋 Columns in job_applications:")
        for col in columns:
            print(f"  - {col['name']}: {col['type']}")
    
    # Test inserting a record (will rollback)
    print("\n🧪 Testing table structure...")
    db = SessionLocal()
    try:
        # Just verify we can query the table
        count = db.query(JobApplication).count()
        print(f"✅ Table is accessible. Current records: {count}")
        return True
    except Exception as e:
        print(f"❌ Error accessing table: {e}")
        return False
    finally:
        db.close()

if __name__ == "__main__":
    print("=" * 60)
    print("JOB APPLICATIONS TABLE VERIFICATION")
    print("=" * 60)
    
    success = verify_and_create_table()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ VERIFICATION COMPLETE - Table is ready!")
    else:
        print("❌ VERIFICATION FAILED - Please check errors above")
    print("=" * 60)
