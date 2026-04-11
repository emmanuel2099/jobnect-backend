from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings

# Create database engine with SQLite support
if settings.DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        settings.DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
else:
    engine = create_engine(settings.DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initialize database with default data"""
    from app.models import JobCategory, City, JobType, JobLevel, EducationLevel, Skill, Designation, AppSetting, Company, Job
    from datetime import date, timedelta
    
    db = SessionLocal()
    try:
        # Check if data already exists
        if db.query(JobCategory).count() > 0:
            print("✅ Master data already exists")
            return
        
        print("🔄 Inserting default master data...")
        
        # Job Categories
        categories = [
            JobCategory(name="IT & Software", icon="💻", description="Technology and software jobs"),
            JobCategory(name="Marketing & Sales", icon="📈", description="Marketing and sales positions"),
            JobCategory(name="Healthcare", icon="🏥", description="Medical and healthcare jobs"),
            JobCategory(name="Education", icon="📚", description="Teaching and education roles"),
            JobCategory(name="Finance & Accounting", icon="💰", description="Finance and accounting positions"),
            JobCategory(name="Engineering", icon="⚙️", description="Engineering jobs"),
            JobCategory(name="Design & Creative", icon="🎨", description="Design and creative roles"),
            JobCategory(name="Customer Service", icon="📞", description="Customer support positions"),
            JobCategory(name="Human Resources", icon="👥", description="HR and recruitment jobs"),
            JobCategory(name="Operations", icon="🔧", description="Operations and logistics"),
        ]
        db.add_all(categories)
        
        # Cities
        cities = [
            City(name="New York", country="USA"),
            City(name="Los Angeles", country="USA"),
            City(name="Chicago", country="USA"),
            City(name="London", country="UK"),
            City(name="Paris", country="France"),
            City(name="Tokyo", country="Japan"),
            City(name="Dubai", country="UAE"),
            City(name="Singapore", country="Singapore"),
        ]
        db.add_all(cities)
        
        # Job Types
        job_types = [
            JobType(name="Full Time"),
            JobType(name="Part Time"),
            JobType(name="Contract"),
            JobType(name="Freelance"),
            JobType(name="Internship"),
            JobType(name="Remote"),
        ]
        db.add_all(job_types)
        
        # Job Levels
        job_levels = [
            JobLevel(name="Entry Level"),
            JobLevel(name="Mid Level"),
            JobLevel(name="Senior Level"),
            JobLevel(name="Manager"),
            JobLevel(name="Director"),
            JobLevel(name="Executive"),
        ]
        db.add_all(job_levels)
        
        # Education Levels
        education_levels = [
            EducationLevel(name="High School"),
            EducationLevel(name="Associate Degree"),
            EducationLevel(name="Bachelor Degree"),
            EducationLevel(name="Master Degree"),
            EducationLevel(name="PhD"),
            EducationLevel(name="Diploma"),
            EducationLevel(name="Certificate"),
        ]
        db.add_all(education_levels)
        
        # Skills
        skills = [
            Skill(name="JavaScript"),
            Skill(name="Python"),
            Skill(name="Java"),
            Skill(name="React"),
            Skill(name="Node.js"),
            Skill(name="SQL"),
            Skill(name="Project Management"),
            Skill(name="Communication"),
            Skill(name="Leadership"),
            Skill(name="Problem Solving"),
        ]
        db.add_all(skills)
        
        # Designations
        designations = [
            Designation(name="Software Engineer"),
            Designation(name="Senior Developer"),
            Designation(name="Project Manager"),
            Designation(name="Business Analyst"),
            Designation(name="UI/UX Designer"),
            Designation(name="Data Scientist"),
            Designation(name="Marketing Manager"),
            Designation(name="Sales Executive"),
            Designation(name="HR Manager"),
            Designation(name="Accountant"),
        ]
        db.add_all(designations)
        
        # App Settings
        settings_data = [
            AppSetting(key="app_name", value="JobNect"),
            AppSetting(key="app_version", value="1.0.0"),
            AppSetting(key="dark_logo", value="https://via.placeholder.com/200x50?text=JobNect"),
            AppSetting(key="light_logo", value="https://via.placeholder.com/200x50?text=JobNect"),
        ]
        db.add_all(settings_data)
        
        db.commit()
        print("✅ Default master data inserted")
        
    except Exception as e:
        print(f"❌ Error inserting default data: {e}")
        db.rollback()
    finally:
        db.close()
