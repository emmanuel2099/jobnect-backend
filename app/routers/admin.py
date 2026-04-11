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
