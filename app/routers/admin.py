from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc, text
from datetime import datetime
from typing import Optional
from pydantic import BaseModel

from app.database import get_db
from app.models import User, Job, Company, JobApplication, Notification, JobType, JobLevel

router = APIRouter()

# Schemas for admin operations
class SendNotificationRequest(BaseModel):
    user_id: Optional[int] = None
    user_type: Optional[str] = None  # "applicant", "company", or "all"
    title: str
    message: str
    notification_type: Optional[str] = "general"

# Email Verification Management
@router.get("/email-verification-status")
async def get_email_verification_status(db: Session = Depends(get_db)):
    """Get email verification status for all users"""
    try:
        # Get users with their email verification status
        users = db.query(User).order_by(desc(User.created_at)).all()
        
        verified_users = []
        unverified_users = []
        
        for user in users:
            user_data = {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "phone": user.phone,
                "company": user.company,
                "user_type": user.user_type,
                "email_verified": getattr(user, 'email_verified', False),
                "created_at": user.created_at.isoformat() if user.created_at else None,
                "last_login": user.last_login.isoformat() if hasattr(user, 'last_login') and user.last_login else None
            }
            
            if getattr(user, 'email_verified', False):
                verified_users.append(user_data)
            else:
                unverified_users.append(user_data)
        
        # Get recent email verification attempts
        try:
            recent_otps = db.execute(
                text("""
                    SELECT email, purpose, created_at, expires_at 
                    FROM email_otps 
                    WHERE created_at >= NOW() - INTERVAL '7 days'
                    ORDER BY created_at DESC 
                    LIMIT 50
                """)
            ).fetchall()
            
            recent_attempts = [
                {
                    "email": row[0],
                    "purpose": row[1],
                    "created_at": row[2].isoformat() if row[2] else None,
                    "expires_at": row[3].isoformat() if row[3] else None,
                    "status": "expired" if row[3] and row[3] < datetime.utcnow() else "active"
                }
                for row in recent_otps
            ]
        except Exception as e:
            recent_attempts = []
        
        return {
            "success": True,
            "message": "Email verification status retrieved",
            "data": {
                "summary": {
                    "total_users": len(users),
                    "verified_users": len(verified_users),
                    "unverified_users": len(unverified_users),
                    "verification_rate": round((len(verified_users) / len(users)) * 100, 1) if users else 0
                },
                "verified_users": verified_users,
                "unverified_users": unverified_users,
                "recent_attempts": recent_attempts
            }
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Error retrieving email verification status: {str(e)}",
            "data": {
                "summary": {"total_users": 0, "verified_users": 0, "unverified_users": 0, "verification_rate": 0},
                "verified_users": [],
                "unverified_users": [],
                "recent_attempts": []
            }
        }

@router.post("/resend-verification/{user_id}")
async def resend_verification_email(user_id: int, db: Session = Depends(get_db)):
    """Resend verification email to a specific user"""
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Import email service
        from app.email_service import email_service
        
        # Send verification email
        result = email_service.send_verification_email(
            email=user.email,
            name=user.name
        )
        
        return {
            "success": result["success"],
            "message": f"Verification email {'sent' if result['success'] else 'failed'} for {user.email}",
            "data": result
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Error sending verification email: {str(e)}"
        }

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
    """Delete a user and invalidate their session immediately"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return {"success": False, "message": "User not found", "data": {}}
    
    # Store user info before deletion
    user_email = user.email
    user_name = user.name
    
    # Add to invalidated sessions to force logout
    db.execute(text("""
        INSERT INTO invalidated_sessions (user_id, reason) 
        VALUES (:user_id, 'user_deleted')
    """), {"user_id": user_id})
    
    # Delete the user
    db.delete(user)
    db.commit()
    
    return {
        "success": True, 
        "message": f"User {user_name} ({user_email}) deleted successfully and logged out immediately", 
        "data": {"user_id": user_id, "logged_out": True}
    }

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

@router.patch("/users/{user_id}/deactivate")
async def deactivate_user_account(user_id: int, db: Session = Depends(get_db)):
    """Permanently deactivate a user account"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return {"success": False, "message": "User not found", "data": {}}
    
    user.is_deactivated = True
    user.is_active = False
    user.deactivated_at = datetime.utcnow()
    db.commit()
    
    return {
        "success": True,
        "message": "User account deactivated successfully",
        "data": {
            "isDeactivated": user.is_deactivated,
            "deactivatedAt": user.deactivated_at.isoformat() if user.deactivated_at else None
        }
    }

@router.patch("/users/{user_id}/reactivate")
async def reactivate_user_account(user_id: int, db: Session = Depends(get_db)):
    """Reactivate a deactivated user account"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return {"success": False, "message": "User not found", "data": {}}
    
    user.is_deactivated = False
    user.is_active = True
    user.deactivated_at = None
    db.commit()
    
    return {
        "success": True,
        "message": "User account reactivated successfully",
        "data": {
            "isDeactivated": user.is_deactivated,
            "isActive": user.is_active
        }
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
            "age": resume.age if resume else None,
            "skills": skills,
            "skillsCount": len(skills),
            "isActive": user.is_active,
            "isDeactivated": user.is_deactivated,
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

@router.get("/saved-jobs")
async def get_all_saved_jobs(db: Session = Depends(get_db)):
    """Get all saved/bookmarked jobs across all users"""
    from app.models import Bookmark
    
    bookmarks = db.query(Bookmark).order_by(desc(Bookmark.created_at)).all()
    
    return {
        "success": True,
        "message": f"Found {len(bookmarks)} saved jobs",
        "data": {
            "total": len(bookmarks),
            "savedJobs": [
                {
                    "id": bookmark.id,
                    "userId": bookmark.user_id,
                    "userName": bookmark.user.name if bookmark.user else "N/A",
                    "userEmail": bookmark.user.email if bookmark.user else "N/A",
                    "jobId": bookmark.job_id,
                    "jobTitle": bookmark.job.title if bookmark.job else "N/A",
                    "companyName": bookmark.job.company.name if bookmark.job and bookmark.job.company else "N/A",
                    "savedAt": bookmark.created_at.isoformat() if bookmark.created_at else None
                }
                for bookmark in bookmarks
            ]
        }
    }

@router.get("/chat/conversations")
async def get_all_conversations(db: Session = Depends(get_db)):
    """Get all chat conversations for admin monitoring"""
    from app.models import Conversation, Message
    
    conversations = db.query(Conversation).order_by(desc(Conversation.updated_at)).all()
    
    conv_list = []
    for conv in conversations:
        # Get last message
        last_message = db.query(Message).filter(
            Message.conversation_id == conv.id
        ).order_by(desc(Message.created_at)).first()
        
        # Get message count
        message_count = db.query(Message).filter(
            Message.conversation_id == conv.id
        ).count()
        
        # Get users
        user1 = db.query(User).filter(User.id == conv.user1_id).first()
        user2 = db.query(User).filter(User.id == conv.user2_id).first()
        
        conv_list.append({
            "id": conv.id,
            "user1": {
                "id": user1.id if user1 else None,
                "name": user1.name if user1 else "N/A",
                "userType": user1.user_type if user1 else None
            },
            "user2": {
                "id": user2.id if user2 else None,
                "name": user2.name if user2 else "N/A",
                "userType": user2.user_type if user2 else None
            },
            "messageCount": message_count,
            "lastMessage": last_message.message if last_message else None,
            "lastMessageAt": last_message.created_at.isoformat() if last_message else None,
            "createdAt": conv.created_at.isoformat() if conv.created_at else None
        })
    
    return {
        "success": True,
        "message": f"Found {len(conv_list)} conversations",
        "data": {
            "total": len(conv_list),
            "conversations": conv_list
        }
    }

@router.get("/payments")
async def get_all_payments(db: Session = Depends(get_db)):
    """Get all payments for admin financial tracking with comprehensive analytics"""
    from app.models import Payment
    from sqlalchemy import func, extract
    from datetime import datetime, timedelta
    
    payments = db.query(Payment).order_by(desc(Payment.created_at)).all()
    
    # Calculate revenue analytics - Only COMPLETED payments
    completed_payments = [p for p in payments if p.status == "completed"]
    pending_payments = [p for p in payments if p.status == "pending"]
    failed_payments = [p for p in payments if p.status == "failed"]
    
    total_revenue = sum(p.amount for p in completed_payments)  # Only completed
    
    # Monthly revenue (current month) - Only completed payments
    current_month = datetime.now().month
    current_year = datetime.now().year
    monthly_revenue = sum(
        p.amount for p in completed_payments 
        if p.created_at and p.created_at.month == current_month and p.created_at.year == current_year
    )
    
    # Weekly revenue (last 7 days) - Only completed payments
    week_ago = datetime.now() - timedelta(days=7)
    weekly_revenue = sum(
        p.amount for p in completed_payments 
        if p.created_at and p.created_at >= week_ago
    )
    
    # Average payment - Only completed payments
    average_payment = total_revenue / len(completed_payments) if completed_payments else 0
    
    # Payment methods breakdown - Only completed payments
    payment_methods = {}
    for payment in completed_payments:  # Only completed payments
        method = payment.payment_method or "Unknown"
        if method not in payment_methods:
            payment_methods[method] = {"count": 0, "amount": 0}
        payment_methods[method]["count"] += 1
        payment_methods[method]["amount"] += payment.amount
    
    # Daily revenue for last 7 days
    daily_revenue = {}
    for i in range(7):
        date = datetime.now() - timedelta(days=i)
        date_str = date.strftime("%Y-%m-%d")
        daily_revenue[date_str] = sum(
            p.amount for p in completed_payments 
            if p.created_at and p.created_at.date() == date.date()
        )
    
    return {
        "success": True,
        "message": f"Found {len(payments)} payments",
        "data": {
            "summary": {
                "totalRevenue": total_revenue,
                "monthlyRevenue": monthly_revenue,
                "weeklyRevenue": weekly_revenue,
                "averagePayment": round(average_payment, 2),
                "totalPayments": len(payments),
                "completedPayments": len(completed_payments),
                "pendingPayments": len(pending_payments),
                "failedPayments": len(failed_payments)
            },
            "paymentMethods": payment_methods,
            "dailyRevenue": daily_revenue,
            "payments": [
                {
                    "id": payment.id,
                    "userId": payment.user_id,
                    "userName": db.query(User).filter(User.id == payment.user_id).first().name if db.query(User).filter(User.id == payment.user_id).first() else "N/A",
                    "userEmail": db.query(User).filter(User.id == payment.user_id).first().email if db.query(User).filter(User.id == payment.user_id).first() else "N/A",
                    "amount": payment.amount,
                    "currency": payment.currency,
                    "paymentMethod": payment.payment_method,
                    "transactionReference": payment.transaction_reference,
                    "status": payment.status,
                    "paymentDate": payment.payment_date.isoformat() if payment.payment_date else None,
                    "createdAt": payment.created_at.isoformat() if payment.created_at else None
                }
                for payment in payments
            ]
        }
    }

# Job Type Management
@router.post("/job-types/create")
async def create_job_type(name: str, description: str = "", db: Session = Depends(get_db)):
    """Create a new job type"""
    try:
        job_type = JobType(
            name=name,
            description=description,
            is_active=True
        )
        db.add(job_type)
        db.commit()
        db.refresh(job_type)
        
        return {
            "success": True,
            "message": f"Job type '{name}' created successfully",
            "data": {
                "id": job_type.id,
                "name": job_type.name,
                "description": job_type.description
            }
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

# Job Level Management
@router.post("/job-levels/create")
async def create_job_level(name: str, description: str = "", db: Session = Depends(get_db)):
    """Create a new job level"""
    try:
        job_level = JobLevel(
            name=name,
            description=description,
            is_active=True
        )
        db.add(job_level)
        db.commit()
        db.refresh(job_level)
        
        return {
            "success": True,
            "message": f"Job level '{name}' created successfully",
            "data": {
                "id": job_level.id,
                "name": job_level.name,
                "description": job_level.description
            }
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
