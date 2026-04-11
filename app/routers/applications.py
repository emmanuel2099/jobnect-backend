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
    
    # Check if job exists
    job = db.query(Job).filter(Job.id == data.job_id).first()
    if not job:
        return {
            "success": False,
            "message": "Job not found",
            "data": {}
        }
    
    # Check if already applied
    existing_application = db.query(JobApplication).filter(
        JobApplication.user_id == current_user.id,
        JobApplication.job_id == data.job_id
    ).first()
    
    if existing_application:
        return {
            "success": False,
            "message": "You have already applied for this job",
            "data": {}
        }
    
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
    
    return {
        "success": True,
        "message": "Application submitted successfully",
        "data": {
            "application_id": application.id,
            "status": application.status
        }
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
