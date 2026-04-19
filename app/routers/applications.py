from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.database import get_db
from app.models import JobApplication, Bookmark, Job, Company, User
from app.schemas import JobApplicationCreate, BookmarkCreate
from app.auth import get_current_user

router = APIRouter()

@router.post("/applicant/job-apply")
async def apply_for_job(data: JobApplicationCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Apply for a job"""
    
    try:
        print(f"📝 Job application request - User: {current_user.id}, Job: {data.job_id}")
        
        # Check if job exists
        job = db.query(Job).filter(Job.id == data.job_id).first()
        if not job:
            print(f"❌ Job {data.job_id} not found")
            return {
                "success": False,
                "message": "Job not found",
                "data": {}
            }
        
        print(f"✅ Job found: {job.title}")
        
        # Check if already applied
        existing_application = db.query(JobApplication).filter(
            JobApplication.user_id == current_user.id,
            JobApplication.job_id == data.job_id
        ).first()
        
        if existing_application:
            print(f"⚠️  User {current_user.id} already applied to job {data.job_id}")
            return {
                "success": False,
                "message": "You have already applied for this job",
                "data": {}
            }
        
        print(f"🔄 Creating application record...")
        
        # Create application
        application = JobApplication(
            user_id=current_user.id,
            job_id=data.job_id,
            cover_letter=data.cover_letter,
            resume_file=data.resume_file,
            status="pending"
        )
        
        db.add(application)
        db.commit()
        db.refresh(application)
        
        print(f"✅ Application created successfully - ID: {application.id}")
        
        return {
            "success": True,
            "message": "Application submitted successfully",
            "data": {
                "application_id": application.id,
                "status": application.status
            }
        }
    except Exception as e:
        db.rollback()
        print(f"❌ Error submitting application: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "message": f"Failed to submit application: {str(e)}",
            "data": {},
            "error_details": str(e)
        }

@router.get("/applicant/job/applied")
async def get_applied_jobs(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get all jobs the user has applied to"""
    
    applications = db.query(JobApplication).filter(
        JobApplication.user_id == current_user.id
    ).order_by(desc(JobApplication.created_at)).all()
    
    applied_jobs = []
    for app in applications:
        job = db.query(Job).filter(Job.id == app.job_id).first()
        if job:
            company = db.query(Company).filter(Company.id == job.company_id).first()
            
            applied_jobs.append({
                "application_id": app.id,
                "status": app.status,
                "applied_at": str(app.created_at),
                "job": {
                    "id": job.id,
                    "title": job.title,
                    "description": job.description,
                    "salary_min": job.salary_min,
                    "salary_max": job.salary_max,
                    "location": job.location,
                    "deadline": str(job.deadline) if job.deadline else None,
                    "company": {
                        "id": company.id,
                        "name": company.name,
                        "logo": company.logo
                    } if company else None
                }
            })
    
    return {
        "success": True,
        "message": "Applied jobs retrieved",
        "data": {"applications": applied_jobs}
    }

@router.get("/applicant/job/bookmarks")
async def get_bookmarked_jobs(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get all bookmarked jobs"""
    
    bookmarks = db.query(Bookmark).filter(
        Bookmark.user_id == current_user.id
    ).order_by(desc(Bookmark.created_at)).all()
    
    bookmarked_jobs = []
    for bookmark in bookmarks:
        job = db.query(Job).filter(Job.id == bookmark.job_id).first()
        if job:
            company = db.query(Company).filter(Company.id == job.company_id).first()
            
            bookmarked_jobs.append({
                "bookmark_id": bookmark.id,
                "bookmarked_at": str(bookmark.created_at),
                "job": {
                    "id": job.id,
                    "title": job.title,
                    "description": job.description,
                    "salary_min": job.salary_min,
                    "salary_max": job.salary_max,
                    "location": job.location,
                    "deadline": str(job.deadline) if job.deadline else None,
                    "company": {
                        "id": company.id,
                        "name": company.name,
                        "logo": company.logo
                    } if company else None
                }
            })
    
    return {
        "success": True,
        "message": "Bookmarked jobs retrieved",
        "data": {"bookmarks": bookmarked_jobs}
    }

@router.post("/applicant/job/bookmark/store")
async def bookmark_job(data: BookmarkCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Bookmark or unbookmark a job"""
    
    # Check if job exists
    job = db.query(Job).filter(Job.id == data.job_id).first()
    if not job:
        return {
            "success": False,
            "message": "Job not found",
            "data": {}
        }
    
    # Check if already bookmarked
    existing_bookmark = db.query(Bookmark).filter(
        Bookmark.user_id == current_user.id,
        Bookmark.job_id == data.job_id
    ).first()
    
    if existing_bookmark:
        # Remove bookmark
        db.delete(existing_bookmark)
        db.commit()
        return {
            "success": True,
            "message": "Bookmark removed",
            "data": {"bookmarked": False}
        }
    else:
        # Add bookmark
        bookmark = Bookmark(
            user_id=current_user.id,
            job_id=data.job_id
        )
        db.add(bookmark)
        db.commit()
        return {
            "success": True,
            "message": "Job bookmarked",
            "data": {"bookmarked": True}
        }

@router.get("/company/applications/recent")
async def get_company_recent_applications(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get recent applications for company's jobs"""
    
    # Find company owned by current user
    company = db.query(Company).filter(Company.user_id == current_user.id).first()
    if not company:
        return {
            "success": True,
            "message": "No company found",
            "data": {"applications": []}
        }
    
    # Get all jobs for this company
    company_jobs = db.query(Job).filter(Job.company_id == company.id).all()
    job_ids = [job.id for job in company_jobs]
    
    # Get recent applications for these jobs
    applications = db.query(JobApplication).filter(
        JobApplication.job_id.in_(job_ids)
    ).order_by(desc(JobApplication.created_at)).limit(10).all()
    
    applications_data = []
    for app in applications:
        job = db.query(Job).filter(Job.id == app.job_id).first()
        applicant = db.query(User).filter(User.id == app.user_id).first()
        
        if job and applicant:
            applications_data.append({
                "id": app.id,
                "status": app.status,
                "cover_letter": app.cover_letter,
                "resume_file": app.resume_file,
                "created_at": str(app.created_at),
                "applicant": {
                    "id": applicant.id,
                    "name": applicant.name,
                    "email": applicant.email,
                    "phone": applicant.phone,
                    "profile_picture": applicant.profile_picture
                },
                "job": {
                    "id": job.id,
                    "title": job.title,
                    "location": job.location
                }
            })
    
    return {
        "success": True,
        "message": "Recent applications retrieved",
        "data": {"applications": applications_data}
    }

@router.get("/company/applications/by-job")
async def get_company_applications_by_job(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get applications grouped by job for company"""
    
    # Find company owned by current user
    company = db.query(Company).filter(Company.user_id == current_user.id).first()
    
    # If no company record exists, check if user is a company type and get jobs directly
    if not company:
        # Check if user is company type
        if current_user.user_type != "company":
            return {
                "success": True,
                "message": "User is not a company",
                "data": {"jobs": []}
            }
        
        # For company users without a Company record, return empty for now
        # In production, you might want to auto-create a Company record here
        return {
            "success": True,
            "message": "No company profile found. Please complete your company profile.",
            "data": {"jobs": []}
        }
    
    # Get all jobs for this company
    jobs = db.query(Job).filter(Job.company_id == company.id).order_by(desc(Job.created_at)).all()
    
    jobs_data = []
    for job in jobs:
        # Get applications for this job
        applications = db.query(JobApplication).filter(
            JobApplication.job_id == job.id
        ).order_by(desc(JobApplication.created_at)).all()
        
        applications_list = []
        for app in applications:
            applicant = db.query(User).filter(User.id == app.user_id).first()
            if applicant:
                applications_list.append({
                    "id": app.id,
                    "status": app.status,
                    "created_at": str(app.created_at),
                    "applicant": {
                        "id": applicant.id,
                        "name": applicant.name,
                        "email": applicant.email,
                        "phone": applicant.phone,
                        "profile_picture": applicant.profile_picture
                    }
                })
        
        jobs_data.append({
            "id": job.id,
            "title": job.title,
            "location": job.location,
            "is_active": job.is_active,
            "applications_count": len(applications_list),
            "applications": applications_list
        })
    
    return {
        "success": True,
        "message": "Applications by job retrieved",
        "data": {"jobs": jobs_data}
    }
