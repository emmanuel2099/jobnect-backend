from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from sqlalchemy import desc, text
from datetime import datetime, timedelta
from typing import Optional
from pydantic import BaseModel
import os

from app.database import get_db
from app.models import User, Job, Company, JobApplication, Notification, JobType, JobLevel, Admin
from app.auth import create_access_token, hash_password, verify_password
from app.config import settings

router = APIRouter()

# ── Admin Auth Schemas ──────────────────────────────────────────────────────
class AdminSignupRequest(BaseModel):
    name: str
    email: str
    password: str
    signup_code: str  # secret code — first admin sets it, subsequent admins must match it

# ── Admin Signup ────────────────────────────────────────────────────────────
@router.post("/signup")
async def admin_signup(request: AdminSignupRequest, db: Session = Depends(get_db)):
    """Register a new admin account.
    - First admin: any signup_code is accepted and becomes the permanent code stored in DB.
    - Subsequent admins: must provide the code set by the first admin.
    """
    from sqlalchemy import text as sqlt

    # Get or set the signup code stored in DB
    try:
        row = db.execute(sqlt("SELECT value FROM admin_settings WHERE key = 'signup_code'")).fetchone()
        stored_code = row[0] if row else None
    except Exception:
        stored_code = None

    first_admin = db.query(Admin).count() == 0

    if first_admin:
        # First admin — store their chosen signup code
        if not request.signup_code or len(request.signup_code) < 6:
            raise HTTPException(status_code=400, detail="Signup code must be at least 6 characters")
        try:
            db.execute(sqlt("""
                INSERT INTO admin_settings (key, value) VALUES ('signup_code', :code)
                ON CONFLICT (key) DO UPDATE SET value = :code
            """), {"code": request.signup_code})
            db.commit()
        except Exception:
            db.rollback()
    else:
        # Subsequent admins — must match stored code
        if not stored_code or request.signup_code != stored_code:
            raise HTTPException(status_code=403, detail="Invalid signup code")

    existing = db.query(Admin).filter(Admin.email == request.email).first()
    if existing:
        return {"success": False, "message": "Email already registered as admin"}

    new_admin = Admin(
        name=request.name,
        email=request.email,
        password=hash_password(request.password),
        is_active=True,
    )
    db.add(new_admin)
    db.commit()
    db.refresh(new_admin)

    token = create_access_token(
        data={"sub": new_admin.email, "user_id": new_admin.id, "user_type": "admin"},
        expires_delta=timedelta(hours=12)
    )
    return {
        "success": True,
        "message": "Admin account created successfully",
        "data": {"token": token, "name": new_admin.name, "email": new_admin.email}
    }

# ── Admin Login ─────────────────────────────────────────────────────────────
@router.post("/login")
async def admin_login(request: AdminLoginRequest, db: Session = Depends(get_db)):
    """Admin login"""
    admin = db.query(Admin).filter(Admin.email == request.email).first()
    if not admin or not verify_password(request.password, admin.password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    if not admin.is_active:
        raise HTTPException(status_code=403, detail="Admin account is deactivated")

    admin.last_login = datetime.utcnow()
    db.commit()

    token = create_access_token(
        data={"sub": admin.email, "user_id": admin.id, "user_type": "admin"},
        expires_delta=timedelta(hours=12)
    )
    return {
        "success": True,
        "message": "Login successful",
        "data": {"token": token, "name": admin.name, "email": admin.email}
    }

# ── Token Verify ─────────────────────────────────────────────────────────────
@router.get("/verify-token")
async def verify_admin_token(request: Request):
    """Verify admin token is valid"""
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="No token provided")

    from jose import JWTError, jwt
    try:
        token = auth.split(" ")[1]
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        if payload.get("user_type") != "admin":
            raise HTTPException(status_code=403, detail="Not an admin token")
        return {"success": True, "message": "Token valid", "name": payload.get("sub")}
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

# ── Delete All Users ──────────────────────────────────────────────────────────
@router.delete("/delete-all-users")
async def delete_all_users(request: Request, db: Session = Depends(get_db)):
    """Delete ALL job seekers and company users (irreversible — admin only)"""
    from jose import JWTError, jwt
    from app.models import JobSeeker, CompanyUser

    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="No token provided")
    try:
        token = auth.split(" ")[1]
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        if payload.get("user_type") != "admin":
            raise HTTPException(status_code=403, detail="Admin access required")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    try:
        js_count = db.query(JobSeeker).count()
        cu_count = db.query(CompanyUser).count()
        db.query(JobSeeker).delete(synchronize_session=False)
        db.query(CompanyUser).delete(synchronize_session=False)
        db.commit()
        return {
            "success": True,
            "message": f"Deleted {js_count} job seekers and {cu_count} company users",
            "data": {"job_seekers_deleted": js_count, "companies_deleted": cu_count}
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Delete failed: {str(e)}")
class AdminPostJobRequest(BaseModel):
    title: str
    company_name: str
    description: str
    requirements: Optional[str] = None
    responsibilities: Optional[str] = None
    location: str
    job_type: Optional[str] = None
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    currency: Optional[str] = "NGN"
    vacancies: Optional[int] = 1
    deadline: Optional[str] = None
    experience_required: Optional[str] = None
    category_id: Optional[int] = None

@router.post("/post-job")
async def admin_post_job(request: Request, job: AdminPostJobRequest, db: Session = Depends(get_db)):
    """Admin posts a job — creates or reuses an admin company record"""
    from jose import JWTError, jwt
    from app.models import Company, Job, JobCategory

    # Verify admin token
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="No token provided")
    try:
        token = auth.split(" ")[1]
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        if payload.get("user_type") != "admin":
            raise HTTPException(status_code=403, detail="Admin access required")
        admin_id = payload.get("user_id")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    # Find or create a company record for this admin post
    company = db.query(Company).filter(Company.name == job.company_name).first()
    if not company:
        company = Company(
            name=job.company_name,
            is_active=True,
        )
        db.add(company)
        db.commit()
        db.refresh(company)

    # Resolve deadline
    deadline = None
    if job.deadline:
        try:
            from datetime import date
            deadline = date.fromisoformat(job.deadline)
        except Exception:
            pass

    new_job = Job(
        title=job.title,
        description=job.description,
        requirements=job.requirements,
        responsibilities=job.responsibilities,
        location=job.location,
        salary_min=job.salary_min,
        salary_max=job.salary_max,
        currency=job.currency or "NGN",
        vacancies=job.vacancies or 1,
        deadline=deadline,
        experience_required=job.experience_required,
        category_id=job.category_id,
        company_id=company.id,
        is_active=True,
        created_at=datetime.utcnow(),
    )
    db.add(new_job)
    db.commit()
    db.refresh(new_job)

    return {
        "success": True,
        "message": f"Job '{new_job.title}' posted successfully",
        "data": {"job_id": new_job.id, "title": new_job.title, "company": company.name}
    }

# ── Signup Info (for UI hint) ─────────────────────────────────────────────
@router.get("/signup-info")
async def signup_info(db: Session = Depends(get_db)):
    """Tell the UI if this is the first admin signup"""
    is_first = db.query(Admin).count() == 0
    return {"success": True, "is_first_admin": is_first}

# ── Other Admin Schemas ──────────────────────────────────────────────────────
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


# ============================================================
# ADMIN AUTH - Login, Signup, Logout
# ============================================================

ADMIN_CREDENTIALS = {
    "email": "admin@eaglespride.com",
    "password": "EagleAdmin2024!"
}

class AdminLoginRequest(BaseModel):
    email: str
    password: str

class AdminSignupRequest(BaseModel):
    email: str
    password: str
    secret_key: str  # Required to prevent unauthorized admin creation

ADMIN_SECRET_KEY = "EAGLES_PRIDE_ADMIN_2024"

@router.post("/auth/signup")
async def admin_signup(data: AdminSignupRequest):
    """Create admin account (requires secret key)"""
    if data.secret_key != ADMIN_SECRET_KEY:
        raise HTTPException(status_code=403, detail="Invalid secret key")
    # In production, store in DB. For now, just confirm credentials match
    return {
        "success": True,
        "message": "Admin account confirmed",
        "data": {"email": data.email}
    }

@router.post("/auth/login")
async def admin_login(data: AdminLoginRequest):
    """Admin login - returns JWT token"""
    from app.auth import create_access_token, hash_password
    import bcrypt

    if data.email != ADMIN_CREDENTIALS["email"]:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Simple password check
    if data.password != ADMIN_CREDENTIALS["password"]:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token(data={"sub": data.email, "user_id": 0, "user_type": "admin"})
    return {
        "success": True,
        "message": "Admin login successful",
        "data": {
            "token": token,
            "token_type": "bearer",
            "user": {"email": data.email, "role": "admin"}
        }
    }

@router.post("/auth/logout")
async def admin_logout():
    """Admin logout"""
    return {"success": True, "message": "Logged out successfully"}


# ============================================================
# ADMIN POST JOB + PUSH NOTIFICATION
# ============================================================

class AdminJobCreate(BaseModel):
    title: str
    description: str
    requirements: str = ""
    responsibilities: str = ""
    location: str = ""
    salary_min: float = 0
    salary_max: float = 0
    job_type_id: int = 1
    job_level_id: int = 1
    category_id: int = 1
    deadline: str = ""
    vacancies: int = 1
    send_notification: bool = True

@router.post("/jobs/post")
async def admin_post_job(data: AdminJobCreate, db: Session = Depends(get_db)):
    """Admin posts a job and optionally sends push notification to all users"""
    from app.models import JobCategory
    from datetime import datetime as dt

    # Get or create admin company
    admin_company = db.query(Company).filter(Company.name == "Eagle's Pride Admin").first()
    if not admin_company:
        admin_company = Company(
            name="Eagle's Pride Admin",
            email="admin@eaglespride.com",
            phone="00000000000",
            is_active=True
        )
        db.add(admin_company)
        db.commit()
        db.refresh(admin_company)

    # Parse deadline
    deadline_date = None
    if data.deadline:
        try:
            deadline_date = dt.strptime(data.deadline, "%Y-%m-%d").date()
        except:
            pass

    job = Job(
        company_id=admin_company.id,
        title=data.title,
        description=data.description,
        requirements=data.requirements,
        responsibilities=data.responsibilities,
        location=data.location,
        salary_min=data.salary_min,
        salary_max=data.salary_max,
        job_type_id=data.job_type_id,
        job_level_id=data.job_level_id,
        category_id=data.category_id,
        deadline=deadline_date,
        vacancies=data.vacancies,
        is_active=True
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    push_sent = 0
    if data.send_notification:
        # Send FCM push notification to all job seekers
        try:
            from app.fcm_service import send_job_alert_to_all
            push_sent = send_job_alert_to_all(db, data.title, "Eagle's Pride", job.id, data.location)
        except Exception as e:
            print(f"FCM error: {e}")

        # Also create in-app notifications
        try:
            from app.notification_service import notify_new_job_posted
            notify_new_job_posted(db, job.id)
        except Exception as e:
            print(f"In-app notification error: {e}")

    return {
        "success": True,
        "message": f"Job posted successfully. Push notifications sent to {push_sent} devices.",
        "data": {"job_id": job.id, "push_notifications_sent": push_sent}
    }


# ============================================================
# BULK DELETE USERS
# ============================================================

@router.delete("/users/delete-all")
async def delete_all_users(user_type: str = "all", db: Session = Depends(get_db)):
    """Delete all users. user_type: 'all', 'job_seekers', or 'companies'"""
    from app.models import JobSeeker, CompanyUser
    deleted = 0

    try:
        if user_type in ("all", "job_seekers"):
            count = db.query(JobSeeker).count()
            db.query(JobSeeker).delete()
            deleted += count

        if user_type in ("all", "companies"):
            count = db.query(CompanyUser).count()
            db.query(CompanyUser).delete()
            deleted += count

        if user_type == "all":
            count = db.query(User).count()
            db.query(User).delete()
            deleted += count

        db.commit()
        return {"success": True, "message": f"Deleted {deleted} users", "deleted_count": deleted}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/users/delete-bulk")
async def delete_bulk_users(user_ids: list, db: Session = Depends(get_db)):
    """Delete multiple users by ID list"""
    from app.models import JobSeeker, CompanyUser
    deleted = 0

    try:
        for uid in user_ids:
            for model in [JobSeeker, CompanyUser, User]:
                user = db.query(model).filter(model.id == uid).first()
                if user:
                    db.delete(user)
                    deleted += 1
                    break
        db.commit()
        return {"success": True, "message": f"Deleted {deleted} users", "deleted_count": deleted}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/jobs/delete-all")
async def delete_all_jobs(db: Session = Depends(get_db)):
    """Delete all job postings"""
    try:
        count = db.query(Job).count()
        db.query(Job).delete()
        db.commit()
        return {"success": True, "message": f"Deleted {count} jobs", "deleted_count": count}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/notifications/send-push-all")
async def send_push_to_all_users(
    title: str,
    message: str,
    db: Session = Depends(get_db)
):
    """Send push notification to ALL users (job seekers + companies)"""
    from app.models import JobSeeker, CompanyUser
    from app.fcm_service import send_notification_to_multiple

    tokens = []
    for js in db.query(JobSeeker).filter(JobSeeker.fcm_token != None).all():
        if js.fcm_token:
            tokens.append(js.fcm_token)
    for cu in db.query(CompanyUser).filter(CompanyUser.fcm_token != None).all():
        if cu.fcm_token:
            tokens.append(cu.fcm_token)

    sent = send_notification_to_multiple(tokens, title, message, {"type": "admin_broadcast"})
    return {"success": True, "message": f"Sent to {sent}/{len(tokens)} devices", "sent": sent, "total": len(tokens)}
