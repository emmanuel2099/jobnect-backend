"""
Debug script to check job applications in database
"""
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Database connection
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://jobnect_db_user:Aq0qlYxqxqJqGPqxqxqxqxqxqxqxqxqx@dpg-ctlabcdefghijk-a.oregon-postgres.render.com/jobnect_db")

# Fix for SQLAlchemy 1.4+ with Render PostgreSQL
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def debug_applications():
    db = SessionLocal()
    
    try:
        print("\n" + "="*60)
        print("🔍 DEBUGGING JOB APPLICATIONS")
        print("="*60)
        
        # Check all users
        print("\n📋 ALL USERS:")
        users = db.execute(text("SELECT id, name, email, user_type FROM users ORDER BY id")).fetchall()
        for user in users:
            print(f"  User {user[0]}: {user[1]} ({user[2]}) - Type: {user[3]}")
        
        # Check all companies
        print("\n🏢 ALL COMPANIES:")
        companies = db.execute(text("SELECT id, user_id, name FROM companies ORDER BY id")).fetchall()
        for company in companies:
            print(f"  Company {company[0]}: {company[2]} (User ID: {company[1]})")
        
        # Check all jobs
        print("\n💼 ALL JOBS:")
        jobs = db.execute(text("SELECT id, company_id, title, is_active FROM jobs ORDER BY id")).fetchall()
        for job in jobs:
            print(f"  Job {job[0]}: {job[2]} (Company ID: {job[1]}, Active: {job[3]})")
        
        # Check all applications
        print("\n📝 ALL JOB APPLICATIONS:")
        applications = db.execute(text("""
            SELECT ja.id, ja.user_id, ja.job_id, ja.status, ja.created_at,
                   u.name as applicant_name, j.title as job_title
            FROM job_applications ja
            LEFT JOIN users u ON ja.user_id = u.id
            LEFT JOIN jobs j ON ja.job_id = j.id
            ORDER BY ja.id
        """)).fetchall()
        
        if not applications:
            print("  ❌ NO APPLICATIONS FOUND!")
        else:
            for app in applications:
                print(f"  Application {app[0]}: {app[5]} applied to '{app[6]}' (Job ID: {app[2]}, Status: {app[3]})")
        
        # Check company-job-application relationship
        print("\n🔗 COMPANY → JOBS → APPLICATIONS:")
        company_data = db.execute(text("""
            SELECT c.id, c.name, c.user_id,
                   COUNT(DISTINCT j.id) as job_count,
                   COUNT(ja.id) as application_count
            FROM companies c
            LEFT JOIN jobs j ON j.company_id = c.id
            LEFT JOIN job_applications ja ON ja.job_id = j.id
            GROUP BY c.id, c.name, c.user_id
            ORDER BY c.id
        """)).fetchall()
        
        for row in company_data:
            print(f"  Company {row[0]} ({row[1]}, User: {row[2]}): {row[3]} jobs, {row[4]} applications")
        
        print("\n" + "="*60)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    debug_applications()
