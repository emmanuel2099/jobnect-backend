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
        
        # Add sample companies
        print("🔄 Adding sample companies...")
        companies_data = [
            Company(name="Tech Corp", industry="Technology", location="New York", company_size="100-500", is_featured=True, is_active=True),
            Company(name="Digital Solutions", industry="IT Services", location="San Francisco", company_size="50-100", is_featured=True, is_active=True),
            Company(name="Global Marketing Inc", industry="Marketing", location="London", company_size="500-1000", is_featured=False, is_active=True),
            Company(name="Healthcare Plus", industry="Healthcare", location="Chicago", company_size="1000+", is_featured=True, is_active=True),
            Company(name="Finance Pro", industry="Finance", location="New York", company_size="200-500", is_featured=False, is_active=True),
        ]
        db.add_all(companies_data)
        db.commit()
        print("✅ Sample companies added")
        
        # Add sample jobs
        print("🔄 Adding sample jobs...")
        jobs_data = [
            Job(
                company_id=1, category_id=1, city_id=1, job_type_id=1, job_level_id=2,
                title="Senior Software Engineer",
                description="We are looking for an experienced software engineer...",
                requirements="5+ years experience, Python, React",
                responsibilities="Develop and maintain applications",
                salary_min=80000, salary_max=120000,
                location="New York, NY",
                deadline=date.today() + timedelta(days=30),
                vacancies=3,
                experience_required="5+ years",
                is_active=True
            ),
            Job(
                company_id=2, category_id=1, city_id=2, job_type_id=6, job_level_id=2,
                title="Full Stack Developer (Remote)",
                description="Join our remote team as a full stack developer...",
                requirements="3+ years experience, JavaScript, Node.js, React",
                responsibilities="Build web applications",
                salary_min=70000, salary_max=100000,
                location="Remote",
                deadline=date.today() + timedelta(days=45),
                vacancies=2,
                experience_required="3+ years",
                is_active=True
            ),
            Job(
                company_id=3, category_id=2, city_id=4, job_type_id=1, job_level_id=3,
                title="Marketing Manager",
                description="Lead our marketing team...",
                requirements="7+ years in marketing",
                responsibilities="Develop marketing strategies",
                salary_min=90000, salary_max=130000,
                location="London, UK",
                deadline=date.today() + timedelta(days=20),
                vacancies=1,
                experience_required="7+ years",
                is_active=True
            ),
            Job(
                company_id=4, category_id=3, city_id=3, job_type_id=1, job_level_id=2,
                title="Registered Nurse",
                description="Join our healthcare team...",
                requirements="RN license, 2+ years experience",
                responsibilities="Patient care and support",
                salary_min=60000, salary_max=85000,
                location="Chicago, IL",
                deadline=date.today() + timedelta(days=15),
                vacancies=5,
                experience_required="2+ years",
                is_active=True
            ),
            Job(
                company_id=5, category_id=5, city_id=1, job_type_id=1, job_level_id=1,
                title="Junior Accountant",
                description="Entry level accounting position...",
                requirements="Bachelor's degree in Accounting",
                responsibilities="Financial reporting and analysis",
                salary_min=45000, salary_max=60000,
                location="New York, NY",
                deadline=date.today() + timedelta(days=25),
                vacancies=2,
                experience_required="0-2 years",
                is_active=True
            ),
        ]
        db.add_all(jobs_data)
        db.commit()
        print("✅ Sample jobs added")
        
    except Exception as e:
        print(f"❌ Error inserting default data: {e}")
        db.rollback()
    finally:
        db.close()
