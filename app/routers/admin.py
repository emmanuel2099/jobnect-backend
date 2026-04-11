from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, Job, Company, JobApplication

router = APIRouter()

# User Management
@router.delete("/users/{user_id}")
async def delete_user(user_id: int, db: Session = Depends(get_db)):
    """Delete a user"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return {"success": False, "message": "User not found", "data": {}}
    
    db.delete(user)
    db.commit()
    
    return {"success": True, "message": "User deleted successfully", "data": {}}

@router.patch("/users/{user_id}/toggle-status")
async def toggle_user_status(user_id: int, db: Session = Depends(get_db)):
    """Activate/Deactivate a user"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return {"success": False, "message": "User not found", "data": {}}
    
    user.is_active = not user.is_active
    db.commit()
    
    return {
        "success": True,
        "message": f"User {'activated' if user.is_active else 'deactivated'} successfully",
        "data": {"isActive": user.is_active}
    }

# Job Management
@router.delete("/jobs/{job_id}")
async def delete_job(job_id: int, db: Session = Depends(get_db)):
    """Delete a job"""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        return {"success": False, "message": "Job not found", "data": {}}
    
    db.delete(job)
    db.commit()
    
    return {"success": True, "message": "Job deleted successfully", "data": {}}

@router.patch("/jobs/{job_id}/toggle-status")
async def toggle_job_status(job_id: int, db: Session = Depends(get_db)):
    """Activate/Deactivate a job"""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        return {"success": False, "message": "Job not found", "data": {}}
    
    job.is_active = not job.is_active
    db.commit()
    
    return {
        "success": True,
        "message": f"Job {'activated' if job.is_active else 'deactivated'} successfully",
        "data": {"isActive": job.is_active}
    }


# Company Management
@router.delete("/companies/{company_id}")
async def delete_company(company_id: int, db: Session = Depends(get_db)):
    """Delete a company"""
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        return {"success": False, "message": "Company not found", "data": {}}
    
    db.delete(company)
    db.commit()
    
    return {"success": True, "message": "Company deleted successfully", "data": {}}

@router.patch("/companies/{company_id}/toggle-status")
async def toggle_company_status(company_id: int, db: Session = Depends(get_db)):
    """Activate/Deactivate a company"""
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        return {"success": False, "message": "Company not found", "data": {}}
    
    company.is_active = not company.is_active
    db.commit()
    
    return {
        "success": True,
        "message": f"Company {'activated' if company.is_active else 'deactivated'} successfully",
        "data": {"isActive": company.is_active}
    }

# Application Management
@router.delete("/applications/{application_id}")
async def delete_application(application_id: int, db: Session = Depends(get_db)):
    """Delete an application"""
    application = db.query(JobApplication).filter(JobApplication.id == application_id).first()
    if not application:
        return {"success": False, "message": "Application not found", "data": {}}
    
    db.delete(application)
    db.commit()
    
    return {"success": True, "message": "Application deleted successfully", "data": {}}

# Get all applications
@router.get("/applications")
async def get_all_applications(db: Session = Depends(get_db)):
    """Get all job applications"""
    applications = db.query(JobApplication).all()
    
    return {
        "success": True,
        "message": "Applications retrieved successfully",
        "data": {
            "applications": [
                {
                    "id": app.id,
                    "userId": app.user_id,
                    "userName": app.user.name if app.user else "N/A",
                    "userEmail": app.user.email if app.user else "N/A",
                    "jobId": app.job_id,
                    "jobTitle": app.job.title if app.job else "N/A",
                    "status": app.status,
                    "createdAt": app.created_at.isoformat() if app.created_at else None
                }
                for app in applications
            ]
        }
    }
