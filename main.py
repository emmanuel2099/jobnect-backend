from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import uvicorn
import os

from app.database import engine, Base, init_db
from app.routers import auth, profile, jobs, applications, companies, master_data, admin, notifications

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🔄 Creating database tables...")
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created")
    except Exception as e:
        print(f"⚠️  Warning: Could not create tables: {e}")
    
    print("🔄 Initializing default data...")
    try:
        init_db()
        print("✅ Default data initialized")
    except Exception as e:
        print(f"⚠️  Warning: Could not initialize default data: {e}")
    
    yield
    
    # Shutdown
    print("👋 Shutting down...")

app = FastAPI(
    title="JobNect API",
    description="Complete REST API for JobNect Mobile Application",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include routers
app.include_router(auth.router, prefix="/api/v10", tags=["Authentication"])
app.include_router(profile.router, prefix="/api/v10", tags=["Profile & Resume"])
app.include_router(jobs.router, prefix="/api/v10", tags=["Jobs"])
app.include_router(applications.router, prefix="/api/v10", tags=["Applications"])
app.include_router(companies.router, prefix="/api/v10", tags=["Companies"])
app.include_router(master_data.router, prefix="/api/v10", tags=["Master Data"])
app.include_router(notifications.router, prefix="/api/v10", tags=["Notifications"])
app.include_router(admin.router, prefix="/api/v10/admin", tags=["Admin"])

@app.get("/")
async def root():
    return {
        "message": "🎉 JobNect Python API is running!",
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
