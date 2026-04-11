from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn

from app.database import engine, Base, init_db
from app.routers import auth, profile, jobs, applications, companies, master_data

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🔄 Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created")
    
    print("🔄 Initializing default data...")
    init_db()
    print("✅ Default data initialized")
    
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

# Include routers
app.include_router(auth.router, prefix="/api/v10", tags=["Authentication"])
app.include_router(profile.router, prefix="/api/v10", tags=["Profile & Resume"])
app.include_router(jobs.router, prefix="/api/v10", tags=["Jobs"])
app.include_router(applications.router, prefix="/api/v10", tags=["Applications"])
app.include_router(companies.router, prefix="/api/v10", tags=["Companies"])
app.include_router(master_data.router, prefix="/api/v10", tags=["Master Data"])

@app.get("/")
async def root():
    return {
        "message": "🎉 JobNect Python API is running!",
        "version": "1.0.0",
        "status": "active",
        "framework": "FastAPI",
        "documentation": "/docs",
        "endpoints": {
            "auth": "POST /api/v10/registration, POST /api/v10/login",
            "profile": "GET /api/v10/applicant/resume/details",
            "jobs": "GET /api/v10/jobs/recent, GET /api/v10/jobs/popular",
            "applications": "POST /api/v10/applicant/job-apply",
            "companies": "GET /api/v10/companies",
            "master_data": "GET /api/v10/job-category, GET /api/v10/cities"
        }
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
