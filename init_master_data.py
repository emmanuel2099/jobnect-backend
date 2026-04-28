"""
Direct database initialization script for master data
This script directly adds job types, job levels, and categories to the database
"""

import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add the app directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.models import JobType, JobLevel, JobCategory
from app.config import settings

def init_master_data():
    """Initialize master data directly in the database"""
    
    # Create database connection
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Job Types to initialize
        job_types = [
            {"name": "FULL-TIME", "description": "Full-time employment"},
            {"name": "PART-TIME", "description": "Part-time employment"},
            {"name": "CONTRACT", "description": "Contract work"},
            {"name": "INTERNSHIP", "description": "Internship position"},
            {"name": "REMOTE", "description": "Remote work"},
            {"name": "HYBRID", "description": "Hybrid work"}
        ]
        
        # Job Levels to initialize
        job_levels = [
            {"name": "ENTRY-LEVEL", "description": "Entry level position"},
            {"name": "MID-LEVEL", "description": "Mid-level position"},
            {"name": "SENIOR-LEVEL", "description": "Senior level position"},
            {"name": "MANAGER", "description": "Manager position"},
            {"name": "DIRECTOR", "description": "Director position"},
            {"name": "EXECUTIVE", "description": "Executive position"}
        ]
        
        # Categories to initialize
        categories = [
            {"name": "Technology", "icon": "💻", "description": "Technology and IT jobs"},
            {"name": "Marketing", "icon": "📱", "description": "Marketing and advertising"},
            {"name": "Design", "icon": "🎨", "description": "Design and creative work"},
            {"name": "Finance", "icon": "💰", "description": "Finance and accounting"},
            {"name": "Hospitality", "icon": "🏨", "description": "Hotel and restaurant jobs"},
            {"name": "Sales", "icon": "📊", "description": "Sales and business development"},
            {"name": "Healthcare", "icon": "🏥", "description": "Healthcare and medical"},
            {"name": "Education", "icon": "📚", "description": "Education and training"}
        ]
        
        print("🚀 Initializing Job Types...")
        
        # Initialize job types
        for job_type_data in job_types:
            existing = db.query(JobType).filter(JobType.name == job_type_data["name"]).first()
            if not existing:
                job_type = JobType(
                    name=job_type_data["name"],
                    description=job_type_data["description"],
                    is_active=True
                )
                db.add(job_type)
                print(f"✅ Created job type: {job_type_data['name']}")
            else:
                print(f"⚠️  Job type already exists: {job_type_data['name']}")
        
        print("\n🚀 Initializing Job Levels...")
        
        # Initialize job levels
        for job_level_data in job_levels:
            existing = db.query(JobLevel).filter(JobLevel.name == job_level_data["name"]).first()
            if not existing:
                job_level = JobLevel(
                    name=job_level_data["name"],
                    description=job_level_data["description"],
                    is_active=True
                )
                db.add(job_level)
                print(f"✅ Created job level: {job_level_data['name']}")
            else:
                print(f"⚠️  Job level already exists: {job_level_data['name']}")
        
        print("\n🚀 Initializing Categories...")
        
        # Initialize categories
        for category_data in categories:
            existing = db.query(JobCategory).filter(JobCategory.name == category_data["name"]).first()
            if not existing:
                category = JobCategory(
                    name=category_data["name"],
                    icon=category_data["icon"],
                    description=category_data["description"],
                    is_active=True
                )
                db.add(category)
                print(f"✅ Created category: {category_data['name']}")
            else:
                print(f"⚠️  Category already exists: {category_data['name']}")
        
        # Commit all changes
        db.commit()
        print("\n✅ Master data initialization complete!")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    init_master_data()
