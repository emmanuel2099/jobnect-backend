from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import datetime
from typing import Optional
from pydantic import BaseModel

from app.database import get_db
from app.models import User, Job, Company, JobApplication, Notification

router = APIRouter()

# Schemas for admin operations
class SendNotificationRequest(BaseModel):
    user_id: Optional[int] = None
    user_type: Optional[str] = None  # "applicant", "company", or "all"
    title: str
    message: str
    notification_type: Optional[str] = "general"

# User Management
@router.get("/users")
async def get_all_users(
    user_type: Optional[str] = None,
    is_online: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """Get all users with optional filters"""
    query = db.query(User)
    
    if user_type:
        query = query.filter(User.user_type == user_type)
    
    if is_online is not None:
        query = query.filter(User.is_online == is_online)
    
    users = query.order_by(desc(User.created_at)).all()
    
    return {
        "success": True,
        "message": f"Found {len(users)} users",
        "data": {
            "total": len(users),
            "users": [
                {
                    "id": user.id,
                    "name": user.name,
                    "email": user.email,
                    "phone": user.phone,
                    "company": user.company,
                    "userType": user.user_type,
                    "isActive": user.is_active,
                    "isOnline": user.is_online,
                    "lastLogin": user.last_login.isoformat() if user.last_login else None,
                    "createdAt": user.created_at.isoformat() if user.created_at else None
                }
                for user in users
            ]
        }
    }

@router.get("/users/stats")
async def get_user_stats(db: Session = Depends(get_db)):
    """Get user statistics"""
    total_users = db.query(User).count()
    applicants = db.query(User).filter(User.user_type == "applicant").count()
    companies = db.query(User).filter(User.user_type == "company").count()
    online_users = db.query(User).filter(User.is_online == True).count()
    active_users = db.query(User).filter(User.is_active == True).count()
    
    return {
        "success": True,
        "message": "User statistics retrieved",
        "data": {
            "totalUsers": total_users,
            "applicants": applicants,
            "companies": companies,
            "onlineUsers": online_users,
            "activeUsers": active_users
        }
    }

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

# Notification Management
@router.post("/notifications/send")
async def send_notification(
    request: SendNotificationRequest,
    db: Session = Depends(get_db)
):
    """Send notification to user(s) - NO FIREBASE REQUIRED"""
    
    target_users = []
    
    # Determine target users
    if request.user_id:
        # Send to specific user
        user = db.query(User).filter(User.id == request.user_id).first()
        if user:
            target_users.append(user)
    elif request.user_type and request.user_type != "all":
        # Send to all users of specific type
        target_users = db.query(User).filter(User.user_type == request.user_type).all()
    else:
        # Send to all users
        target_users = db.query(User).all()
    
    if not target_users:
        return {
            "success": False,
            "message": "No users found to send notification",
            "data": {}
        }
    
    # Create notifications for each user
    notifications_created = 0
    for user in target_users:
        notification = Notification(
            user_id=user.id,
            title=request.title,
            message=request.message,
            notification_type=request.notification_type,
            is_read=False,
            created_at=datetime.utcnow()
        )
        db.add(notification)
        notifications_created += 1
    
    db.commit()
    
    return {
        "success": True,
        "message": f"Notification sent to {notifications_created} user(s)",
        "data": {
            "recipientCount": notifications_created
        }
    }

@router.get("/notifications")
async def get_all_notifications(db: Session = Depends(get_db)):
    """Get all notifications (admin view)"""
    notifications = db.query(Notification).order_by(desc(Notification.created_at)).limit(100).all()
    
    return {
        "success": True,
        "message": "Notifications retrieved",
        "data": {
            "notifications": [
                {
                    "id": notif.id,
                    "userId": notif.user_id,
                    "userName": notif.user.name if notif.user else "N/A",
                    "title": notif.title,
                    "message": notif.message,
                    "type": notif.notification_type,
                    "isRead": notif.is_read,
                    "createdAt": notif.created_at.isoformat() if notif.created_at else None
                }
                for notif in notifications
            ]
        }
    }


# Category Management
@router.get("/categories/manage")
async def get_categories_for_admin(db: Session = Depends(get_db)):
    """Get all categories for admin management"""
    from app.models import JobCategory
    
    categories = db.query(JobCategory).order_by(JobCategory.name).all()
    
    return {
        "success": True,
        "message": f"Found {len(categories)} categories",
        "data": {
            "categories": [
                {
                    "id": cat.id,
                    "name": cat.name,
                    "icon": cat.icon,
                    "description": cat.description,
                    "isActive": cat.is_active,
                    "createdAt": cat.created_at.isoformat() if cat.created_at else None
                }
                for cat in categories
            ]
        }
    }

@router.post("/categories/create")
async def create_category(data: dict, db: Session = Depends(get_db)):
    """Create a new category"""
    from app.models import JobCategory
    
    category = JobCategory(
        name=data.get("name"),
        icon=data.get("icon"),
        description=data.get("description"),
        is_active=data.get("is_active", True)
    )
    
    db.add(category)
    db.commit()
    db.refresh(category)
    
    return {
        "success": True,
        "message": "Category created successfully",
        "data": {"category_id": category.id}
    }

@router.put("/categories/{category_id}")
async def update_category(category_id: int, data: dict, db: Session = Depends(get_db)):
    """Update a category"""
    from app.models import JobCategory
    
    category = db.query(JobCategory).filter(JobCategory.id == category_id).first()
    if not category:
        return {"success": False, "message": "Category not found", "data": {}}
    
    if "name" in data:
        category.name = data["name"]
    if "icon" in data:
        category.icon = data["icon"]
    if "description" in data:
        category.description = data["description"]
    if "is_active" in data:
        category.is_active = data["is_active"]
    
    db.commit()
    
    return {"success": True, "message": "Category updated successfully", "data": {}}

@router.delete("/categories/{category_id}")
async def delete_category(category_id: int, db: Session = Depends(get_db)):
    """Delete a category"""
    from app.models import JobCategory
    
    category = db.query(JobCategory).filter(JobCategory.id == category_id).first()
    if not category:
        return {"success": False, "message": "Category not found", "data": {}}
    
    db.delete(category)
    db.commit()
    
    return {"success": True, "message": "Category deleted successfully", "data": {}}

# Recommended Jobs Management
@router.get("/jobs/recommended/manage")
async def get_jobs_for_recommended(db: Session = Depends(get_db)):
    """Get all jobs with recommended status for admin"""
    jobs = db.query(Job).order_by(desc(Job.created_at)).all()
    
    return {
        "success": True,
        "message": f"Found {len(jobs)} jobs",
        "data": {
            "jobs": [
                {
                    "id": job.id,
                    "title": job.title,
                    "company_id": job.company_id,
                    "location": job.location,
                    "isRecommended": job.is_recommended,
                    "isActive": job.is_active,
                    "createdAt": job.created_at.isoformat() if job.created_at else None
                }
                for job in jobs
            ]
        }
    }

@router.patch("/jobs/{job_id}/toggle-recommended")
async def toggle_job_recommended(job_id: int, db: Session = Depends(get_db)):
    """Toggle recommended status of a job"""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        return {"success": False, "message": "Job not found", "data": {}}
    
    job.is_recommended = not job.is_recommended
    db.commit()
    
    return {
        "success": True,
        "message": f"Job {'added to' if job.is_recommended else 'removed from'} recommended",
        "data": {"isRecommended": job.is_recommended}
    }


# User Profile Details for Admin
@router.get("/users/{user_id}/profile")
async def get_user_profile_details(user_id: int, db: Session = Depends(get_db)):
    """Get complete user profile details including resume, skills, bio, etc."""
    from app.models import Resume, Experience, Education
    import json
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return {"success": False, "message": "User not found", "data": {}}
    
    resume = db.query(Resume).filter(Resume.user_id == user_id).first()
    
    # Parse skills from JSON
    skills = []
    if resume and resume.skills:
        try:
            skills = json.loads(resume.skills)
        except:
            skills = []
    
    # Get experiences
    experiences = []
    if resume:
        experiences = db.query(Experience).filter(Experience.resume_id == resume.id).all()
    
    # Get educations
    educations = []
    if resume:
        educations = db.query(Education).filter(Education.resume_id == resume.id).all()
    
    return {
        "success": True,
        "message": "User profile retrieved",
        "data": {
            "user": {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "phone": user.phone,
                "company": user.company,
                "userType": user.user_type,
                "profilePhoto": user.profile_photo,
                "isActive": user.is_active,
                "isOnline": user.is_online,
                "lastLogin": user.last_login.isoformat() if user.last_login else None,
                "createdAt": user.created_at.isoformat() if user.created_at else None
            },
            "resume": {
                "designation": resume.designation if resume else None,
                "city": resume.city if resume else None,
                "bio": resume.objective if resume else None,
                "skills": skills,
                "dateOfBirth": str(resume.date_of_birth) if resume and resume.date_of_birth else None,
                "gender": resume.gender if resume else None,
                "presentAddress": resume.present_address if resume else None,
                "presentSalary": resume.present_salary if resume else None,
                "expectedSalary": resume.expected_salary if resume else None,
                "jobLevel": resume.job_level if resume else None,
                "jobNature": resume.job_nature if resume else None
            } if resume else None,
            "experiences": [
                {
                    "id": exp.id,
                    "employer": exp.employer,
                    "designation": exp.designation,
                    "department": exp.department,
                    "startDate": str(exp.start_date),
                    "endDate": str(exp.end_date) if exp.end_date else None
                }
                for exp in experiences
            ],
            "educations": [
                {
                    "id": edu.id,
                    "institution": edu.institution,
                    "degree": edu.degree,
                    "level": edu.level,
                    "passingYear": edu.passing_year
                }
                for edu in educations
            ]
        }
    }

@router.get("/users/profiles/all")
async def get_all_user_profiles(
    user_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get all user profiles with basic info for admin dashboard"""
    from app.models import Resume
    import json
    
    query = db.query(User)
    if user_type:
        query = query.filter(User.user_type == user_type)
    
    users = query.order_by(desc(User.created_at)).all()
    
    profiles = []
    for user in users:
        resume = db.query(Resume).filter(Resume.user_id == user.id).first()
        
        # Parse skills
        skills = []
        if resume and resume.skills:
            try:
                skills = json.loads(resume.skills)
            except:
                skills = []
        
        profiles.append({
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "phone": user.phone,
            "userType": user.user_type,
            "profilePhoto": user.profile_photo,
            "designation": resume.designation if resume else None,
            "city": resume.city if resume else None,
            "skills": skills,
            "skillsCount": len(skills),
            "isActive": user.is_active,
            "createdAt": user.created_at.isoformat() if user.created_at else None
        })
    
    return {
        "success": True,
        "message": f"Found {len(profiles)} user profiles",
        "data": {
            "total": len(profiles),
            "profiles": profiles
        }
    }
