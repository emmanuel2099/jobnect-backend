from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from datetime import datetime
import uvicorn
import os

from app.database import engine, Base, init_db
from app.routers import auth, profile, jobs, applications, companies, master_data, admin, notifications, chat, upload, subscriptions, email_verification, feedback, reviews, auth_separate

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup - wrapped in try-catch to show actual errors
    try:
        print("=" * 60)
        print("🚀 STARTING JOBNECT BACKEND")
        print("=" * 60)
        
        # Print all environment variables (without sensitive values)
        print("\n📋 Environment Check:")
        print(f"   DATABASE_URL: {'✅ Set' if os.getenv('DATABASE_URL') else '❌ NOT SET'}")
        print(f"   SECRET_KEY: {'✅ Set' if os.getenv('SECRET_KEY') else '❌ NOT SET'}")
        print(f"   FUNDSVERA_BASE_URL: {'✅ Set' if os.getenv('FUNDSVERA_BASE_URL') else '❌ NOT SET'}")
        print(f"   FUNDSVERA_PUBLIC_KEY: {'✅ Set' if os.getenv('FUNDSVERA_PUBLIC_KEY') else '❌ NOT SET'}")
        print(f"   FUNDSVERA_SECRET_KEY: {'✅ Set' if os.getenv('FUNDSVERA_SECRET_KEY') else '❌ NOT SET'}")
        
        # Check if DATABASE_URL is set
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            print("\n⚠️  WARNING: DATABASE_URL not set!")
            print("⚠️  Database operations will fail.")
            print("⚠️  Please add DATABASE_URL in Render environment variables.")
            print("✅ API server started (database not configured)")
            yield
            return
        
        print(f"\n🔗 Database URL: {database_url[:30]}...")
        
        print("\n🔄 Step 1: Creating database tables...")
        try:
            # Force create all tables
            Base.metadata.create_all(bind=engine, checkfirst=True)
            print("✅ Database tables created successfully")
            
            # Add city column if it doesn't exist
            from sqlalchemy import text
            from app.database import SessionLocal
            db = SessionLocal()
            try:
                # Check if city column exists
                result = db.execute(text("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name='jobs' AND column_name='city';
                """))
                if not result.fetchone():
                    print("🔄 Adding city column to jobs table...")
                    db.execute(text("ALTER TABLE jobs ADD COLUMN city VARCHAR(255);"))
                    db.commit()
                    print("✅ City column added successfully")
                else:
                    print("✅ City column already exists")
                
                # Check if currency column exists
                result = db.execute(text("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name='jobs' AND column_name='currency';
                """))
                if not result.fetchone():
                    print("🔄 Adding currency column to jobs table...")
                    db.execute(text("ALTER TABLE jobs ADD COLUMN currency VARCHAR(10) DEFAULT 'USD';"))
                    db.commit()
                    print("✅ Currency column added successfully")
                else:
                    print("✅ Currency column already exists")
                
                # Check if jobs_applied column exists in subscriptions table
                result = db.execute(text("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name='subscriptions' AND column_name='jobs_applied';
                """))
                if not result.fetchone():
                    print("🔄 Adding jobs_applied column to subscriptions table...")
                    try:
                        db.execute(text("ALTER TABLE subscriptions ADD COLUMN jobs_applied INTEGER DEFAULT 0;"))
                        db.commit()
                        print("✅ jobs_applied column added successfully")
                    except Exception as e:
                        print(f"❌ Error adding jobs_applied column: {e}")
                        # Try alternative approach
                        try:
                            db.execute(text("ALTER TABLE subscriptions ADD COLUMN jobs_applied INTEGER;"))
                            db.execute(text("UPDATE subscriptions SET jobs_applied = 0 WHERE jobs_applied IS NULL;"))
                            db.commit()
                            print("✅ jobs_applied column added successfully (alternative method)")
                        except Exception as e2:
                            print(f"❌ Alternative method also failed: {e2}")
                else:
                    print("✅ jobs_applied column already exists")
                
                # Verify column exists
                result = db.execute(text("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name='subscriptions' AND column_name='jobs_applied';
                """))
                if result.fetchone():
                    print("✅ jobs_applied column verified to exist")
                else:
                    print("❌ jobs_applied column still missing - critical error!")
            except Exception as e:
                print(f"⚠️  Warning: Could not add columns: {e}")
                db.rollback()
            finally:
                db.close()
            
            # Verify critical tables exist
            from sqlalchemy import inspect
            inspector = inspect(engine)
            tables = inspector.get_table_names()
            print(f"📋 Total tables: {len(tables)}")
            
            critical_tables = ['users', 'jobs', 'job_applications', 'companies']
            missing = [t for t in critical_tables if t not in tables]
            if missing:
                print(f"⚠️  WARNING: Missing critical tables: {missing}")
            else:
                print("✅ All critical tables exist")
                
        except Exception as e:
            print(f"❌ ERROR creating tables: {e}")
            print("⚠️  Continuing startup anyway...")
            import traceback
            traceback.print_exc()
        
        print("\n🔄 Step 2: Initializing default data...")
        try:
            from app.database import SessionLocal
            init_db()
            print("✅ Default data initialized")
            
            # Verify data exists
            from app.models import Job, Company
            db = SessionLocal()
            try:
                job_count = db.query(Job).count()
                company_count = db.query(Company).count()
                print(f"📊 Jobs: {job_count}, Companies: {company_count}")
            finally:
                db.close()
                
        except Exception as e:
            print(f"⚠️  Warning: Could not initialize default data: {e}")
            print("⚠️  Continuing startup anyway...")
        
        print("\n" + "=" * 60)
        print("✅ BACKEND READY TO ACCEPT REQUESTS")
        print("=" * 60)
        
        yield
        
    except Exception as e:
        # Catch any startup errors and print them clearly
        print("\n" + "=" * 60)
        print("❌ FATAL ERROR DURING STARTUP")
        print("=" * 60)
        print(f"\nError Type: {type(e).__name__}")
        print(f"Error Message: {str(e)}")
        print("\nFull Traceback:")
        import traceback
        traceback.print_exc()
        print("\n" + "=" * 60)
        print("🔧 TROUBLESHOOTING:")
        print("=" * 60)
        print("1. Check that DATABASE_URL is set in Render environment")
        print("2. Verify database is running and accessible")
        print("3. Check all required environment variables are set")
        print("4. Review the error message above for specific issues")
        print("=" * 60)
        
        # Re-raise the error so Render shows it failed
        raise
    
    # Shutdown
    print("👋 Shutting down...")

app = FastAPI(
    title="JobNect API",
    description="Complete REST API for JobNect Mobile Application",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware - Enhanced for web support
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "*",  # Allow all origins during development
        "http://localhost:*",
        "http://127.0.0.1:*",
        "https://localhost:*",
        "https://127.0.0.1:*",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=[
        "*",
        "Authorization",
        "Content-Type",
        "Accept",
        "Origin",
        "X-Requested-With",
        "Access-Control-Request-Method",
        "Access-Control-Request-Headers",
    ],
    expose_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Root endpoint for health check
@app.get("/")
async def root():
    return {
        "message": "JobNect API is running",
        "version": "1.0.0",
        "status": "healthy",
        "endpoints": {
            "auth": "/api/v10/login",
            "job_seeker_auth": "/api/v10/job-seeker/login",
            "company_auth": "/api/v10/company/login",
            "universal_login": "/api/v10/universal-login",
            "health": "/health"
        }
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }

# Include routers
app.include_router(auth.router, prefix="/api/v10", tags=["Authentication"])
app.include_router(auth_separate.router, prefix="/api/v10", tags=["Separate Authentication"])
app.include_router(profile.router, prefix="/api/v10", tags=["Profile & Resume"])
app.include_router(jobs.router, prefix="/api/v10", tags=["Jobs"])
app.include_router(applications.router, prefix="/api/v10", tags=["Applications"])
app.include_router(companies.router, prefix="/api/v10", tags=["Companies"])
app.include_router(master_data.router, prefix="/api/v10", tags=["Master Data"])
app.include_router(reviews.router, prefix="/api/v10", tags=["Reviews"])
app.include_router(subscriptions.router, prefix="/api/v10", tags=["Subscriptions"])
app.include_router(notifications.router, prefix="/api/v10", tags=["Notifications"])
app.include_router(email_verification.router, prefix="/api/v10", tags=["Email Verification"])
app.include_router(chat.router, tags=["Chat"])
app.include_router(admin.router, prefix="/api/v10/admin", tags=["Admin"])
app.include_router(upload.router, prefix="/api/v10", tags=["Upload"])
app.include_router(feedback.router, prefix="/api/v10", tags=["Feedback"])

@app.get("/")
async def root():
    # Railway redeploy trigger - v2.1
    return {
        "message": "🎉 JobNect Python API is running! (v2.0)",
        "version": "1.0.0",
        "status": "active",
        "framework": "FastAPI",
        "documentation": "/docs",
        "admin_dashboard": "/admin",
        "endpoints": {
            "auth": "POST /api/v10/registration, POST /api/v10/login",
            "profile": "GET /api/v10/applicant/resume/details",
            "jobs": "GET /api/v10/jobs/recent, GET /api/v10/jobs/popular",
            "applications": "POST /api/v10/applicant/job-apply",
            "companies": "GET /api/v10/companies",
            "master_data": "GET /api/v10/job-category, GET /api/v10/cities"
        }
    }

@app.get("/admin", response_class=HTMLResponse)
async def admin_dashboard():
    """Admin Dashboard - Beautiful UI with all features"""
    try:
        with open("templates/admin.html", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return """
        <html><body style="font-family: Arial; padding: 40px; text-align: center;">
        <h1>Admin Dashboard</h1>
        <p>Template file not found. Please ensure templates/admin.html exists.</p>
        <p><a href="/docs">Go to API Documentation</a></p>
        </body></html>
        """

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
