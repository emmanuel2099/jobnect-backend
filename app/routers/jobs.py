from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from typing import Optional

from app.database import get_db
from app.models import Job, Company, JobCategory, City, JobType, JobLevel, User, JobApplication
from app.schemas import JobCreate, JobUpdate
from app.auth import get_current_user
from app.notification_service import notify_new_job_posted

router = APIRouter()

@router.get("/jobs/recent")
async def get_recent_jobs(limit: int = Query(10, ge=1, le=50), db: Session = Depends(get_db)):
    """Get recent jobs"""
    
    jobs = db.query(Job).filter(Job.is_active == True).order_by(desc(Job.created_at)).limit(limit).all()
    
    jobs_data = []
    for job in jobs:
        company = db.query(Company).filter(Company.id == job.company_id).first()
        category = db.query(JobCategory).filter(JobCategory.id == job.category_id).first() if job.category_id else None
        city = db.query(City).filter(City.id == job.city_id).first() if job.city_id else None
        job_type = db.query(JobType).filter(JobType.id == job.job_type_id).first() if job.job_type_id else None
        job_level = db.query(JobLevel).filter(JobLevel.id == job.job_level_id).first() if job.job_level_id else None
        
        jobs_data.append({
            "id": job.id,
            "title": job.title,
            "description": job.description,
            "requirements": job.requirements,
            "responsibilities": job.responsibilities,
            "salary_min": job.salary_min,
            "salary_max": job.salary_max,
            "currency": job.currency if hasattr(job, 'currency') else 'NGN',
            "location": job.location,
            "deadline": str(job.deadline) if job.deadline else None,
            "vacancies": job.vacancies,
            "experience_required": job.experience_required,
            "created_at": str(job.created_at),
            "company": {
                "id": company.id,
                "name": company.name,
                "logo": company.logo,
                "location": company.location
            } if company else None,
            "category": {
                "id": category.id,
                "name": category.name
            } if category else None,
            "city": {
                "id": city.id,
                "name": city.name
            } if city else None,
            "job_type": {
                "id": job_type.id,
                "name": job_type.name
            } if job_type else None,
            "job_level": {
                "id": job_level.id,
                "name": job_level.name
            } if job_level else None
        })
    
    return {
        "success": True,
        "message": "Recent jobs retrieved",
        "data": {"jobs": jobs_data}
    }

@router.get("/jobs/popular")
async def get_popular_jobs(limit: int = Query(10, ge=1, le=50), db: Session = Depends(get_db)):
    """Get popular jobs (most applied)"""
    
    # For now, return recent jobs. In production, track application counts
    jobs = db.query(Job).filter(Job.is_active == True).order_by(desc(Job.created_at)).limit(limit).all()
    
    jobs_data = []
    for job in jobs:
        company = db.query(Company).filter(Company.id == job.company_id).first()
        category = db.query(JobCategory).filter(JobCategory.id == job.category_id).first() if job.category_id else None
        job_type = db.query(JobType).filter(JobType.id == job.job_type_id).first() if job.job_type_id else None
        job_level = db.query(JobLevel).filter(JobLevel.id == job.job_level_id).first() if job.job_level_id else None
        
        jobs_data.append({
            "id": job.id,
            "title": job.title,
            "description": job.description,
            "salary_min": job.salary_min,
            "salary_max": job.salary_max,
            "currency": job.currency if hasattr(job, 'currency') else 'NGN',
            "location": job.location,
            "deadline": str(job.deadline) if job.deadline else None,
            "company": {
                "id": company.id,
                "name": company.name,
                "logo": company.logo
            } if company else None,
            "category": {
                "id": category.id,
                "name": category.name
            } if category else None,
            "job_type": {
                "id": job_type.id,
                "name": job_type.name
            } if job_type else None,
            "job_level": {
                "id": job_level.id,
                "name": job_level.name
            } if job_level else None
        })
    
    return {
        "success": True,
        "message": "Popular jobs retrieved",
        "data": {"jobs": jobs_data}
    }

@router.get("/jobs-filter")
async def filter_jobs(
    category_id: Optional[int] = None,
    city_id: Optional[int] = None,
    job_type_id: Optional[int] = None,
    job_level_id: Optional[int] = None,
    keyword: Optional[str] = None,
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Filter jobs by various criteria"""
    
    query = db.query(Job).filter(Job.is_active == True)
    
    if category_id:
        query = query.filter(Job.category_id == category_id)
    if city_id:
        query = query.filter(Job.city_id == city_id)
    if job_type_id:
        query = query.filter(Job.job_type_id == job_type_id)
    if job_level_id:
        query = query.filter(Job.job_level_id == job_level_id)
    if keyword:
        query = query.filter(
            (Job.title.ilike(f"%{keyword}%")) | 
            (Job.description.ilike(f"%{keyword}%"))
        )
    
    jobs = query.order_by(desc(Job.created_at)).limit(limit).all()
    
    jobs_data = []
    for job in jobs:
        company = db.query(Company).filter(Company.id == job.company_id).first()
        category = db.query(JobCategory).filter(JobCategory.id == job.category_id).first() if job.category_id else None
        
        jobs_data.append({
            "id": job.id,
            "title": job.title,
            "description": job.description,
            "salary_min": job.salary_min,
            "salary_max": job.salary_max,
            "currency": job.currency if hasattr(job, 'currency') else 'NGN',
            "location": job.location,
            "deadline": str(job.deadline) if job.deadline else None,
            "company": {
                "id": company.id,
                "name": company.name,
                "logo": company.logo
            } if company else None,
            "category": {
                "id": category.id,
                "name": category.name
            } if category else None
        })
    
    return {
        "success": True,
        "message": "Filtered jobs retrieved",
        "data": {"jobs": jobs_data, "total": len(jobs_data)}
    }

@router.get("/jobs/details/{job_id}")
async def get_job_details(job_id: int, db: Session = Depends(get_db)):
    """Get detailed job information"""
    
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        return {
            "success": False,
            "message": "Job not found",
            "data": {}
        }
    
    company = db.query(Company).filter(Company.id == job.company_id).first()
    category = db.query(JobCategory).filter(JobCategory.id == job.category_id).first() if job.category_id else None
    city = db.query(City).filter(City.id == job.city_id).first() if job.city_id else None
    job_type = db.query(JobType).filter(JobType.id == job.job_type_id).first() if job.job_type_id else None
    job_level = db.query(JobLevel).filter(JobLevel.id == job.job_level_id).first() if job.job_level_id else None
    
    return {
        "success": True,
        "message": "Job details retrieved",
        "data": {
            "job": {
                "id": job.id,
                "title": job.title,
                "description": job.description,
                "requirements": job.requirements,
                "responsibilities": job.responsibilities,
                "salary_min": job.salary_min,
                "salary_max": job.salary_max,
                "currency": job.currency if hasattr(job, 'currency') else 'NGN',
                "location": job.location,
                "deadline": str(job.deadline) if job.deadline else None,
                "vacancies": job.vacancies,
                "experience_required": job.experience_required,
                "is_active": job.is_active,
                "created_at": str(job.created_at),
                "company": {
                    "id": company.id,
                    "name": company.name,
                    "logo": company.logo,
                    "location": company.location,
                    "description": company.description,
                    "website": company.website
                } if company else None,
                "category": {
                    "id": category.id,
                    "name": category.name
                } if category else None,
                "city": {
                    "id": city.id,
                    "name": city.name
                } if city else None,
                "job_type": {
                    "id": job_type.id,
                    "name": job_type.name
                } if job_type else None,
                "job_level": {
                    "id": job_level.id,
                    "name": job_level.name
                } if job_level else None
            }
        }
    }

@router.get("/job/index")
async def get_company_jobs(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get jobs posted by current company"""
    
    # Find company owned by current user
    company = db.query(Company).filter(Company.user_id == current_user.id).first()
    if not company:
        return {
            "success": True,
            "message": "No company found",
            "data": {"jobs": []}
        }
    
    jobs = db.query(Job).filter(Job.company_id == company.id).order_by(desc(Job.created_at)).all()
    
    jobs_data = []
    for job in jobs:
        # Count applications for this job
        applications_count = db.query(JobApplication).filter(JobApplication.job_id == job.id).count()
        
        jobs_data.append({
            "id": job.id,
            "title": job.title,
            "description": job.description,
            "salary_min": job.salary_min,
            "salary_max": job.salary_max,
            "currency": job.currency if hasattr(job, 'currency') else 'NGN',
            "location": job.location,
            "deadline": str(job.deadline) if job.deadline else None,
            "vacancies": job.vacancies,
            "is_active": job.is_active,
            "created_at": str(job.created_at),
            "applications_count": applications_count
        })
    
    return {
        "success": True,
        "message": "Jobs retrieved",
        "data": {"jobs": jobs_data}
    }

@router.post("/job/store")
async def create_job(data: JobCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Create a new job posting"""
    
    try:
        print(f"\n🔍 CREATE JOB: User {current_user.id} ({current_user.name}) creating job")
        print(f"   Received company_id: {data.company_id}")
        
        # Check subscription before allowing job posting
        from app.subscription_service import SubscriptionService
        
        if data.category_id:
            access_check = SubscriptionService.can_post_job(db, current_user.id, data.category_id)
            if not access_check["allowed"]:
                return {
                    "success": False,
                    "message": access_check["reason"],
                    "requires_payment": access_check.get("requires_payment", False),
                    "plan_needed": access_check.get("plan_needed"),
                    "amount": access_check.get("amount"),
                    "data": {}
                }
            print(f"   ✅ Subscription check passed: {access_check['reason']}")
        
        # First, try to find company by user_id (in case app sent user_id instead of company_id)
        company = db.query(Company).filter(Company.user_id == current_user.id).first()
        
        # If not found, try by company_id
        if not company:
            company = db.query(Company).filter(Company.id == data.company_id, Company.user_id == current_user.id).first()
        
        # If still no company record exists, create one automatically for company users
        if not company:
            if current_user.user_type == "company":
                print(f"   📝 Auto-creating company record for user {current_user.id}")
                # Auto-create company record from user data
                company = Company(
                    user_id=current_user.id,
                    name=current_user.company or current_user.name,
                    email=current_user.email,
                    phone=current_user.phone,
                    logo=current_user.company_logo or current_user.profile_photo,
                    is_active=True
                )
                db.add(company)
                db.commit()
                db.refresh(company)
                print(f"   ✅ Company created: ID={company.id}, Name={company.name}")
            else:
                print(f"   ❌ User is not a company type")
                return {
                    "success": False,
                    "message": "Company not found or unauthorized",
                    "data": {}
                }
        else:
            print(f"   ✅ Found existing company: ID={company.id}, Name={company.name}")
        
        # Parse deadline string to date
        deadline_date = None
        if data.deadline:
            from datetime import datetime
            try:
                # Try parsing YYYY-MM-DD format
                deadline_date = datetime.strptime(data.deadline, "%Y-%m-%d").date()
                print(f"   📅 Deadline parsed (YYYY-MM-DD): {deadline_date}")
            except ValueError:
                try:
                    # Try parsing YYYY-M-D format (without leading zeros)
                    parts = data.deadline.split('-')
                    if len(parts) == 3:
                        year, month, day = int(parts[0]), int(parts[1]), int(parts[2])
                        deadline_date = datetime(year, month, day).date()
                        print(f"   📅 Deadline parsed (YYYY-M-D): {deadline_date}")
                except Exception as e:
                    print(f"   ⚠️  Failed to parse deadline '{data.deadline}': {e}")
        
        print(f"   📝 Creating job: {data.title}")
        job = Job(
            company_id=company.id,
            title=data.title,
            description=data.description,
            requirements=data.requirements,
            responsibilities=data.responsibilities,
            category_id=data.category_id,
            job_type_id=data.job_type_id,
            job_level_id=data.job_level_id,
            salary_min=data.salary_min,
            salary_max=data.salary_max,
            currency=data.currency or 'NGN',  # Save currency
            location=data.location,
            city=data.city,  # Use free text city field
            deadline=deadline_date,
            vacancies=data.vacancies,
            experience_required=data.experience_required,
            is_active=True
        )
        
        db.add(job)
        db.commit()
        db.refresh(job)
        
        print(f"   ✅ Job created successfully: ID={job.id}\n")
        
        # Send notifications to all job seekers
        try:
            notify_new_job_posted(db, job.id)
            print(f"   📬 Notifications sent to job seekers")
        except Exception as notif_error:
            print(f"   ⚠️  Failed to send notifications: {notif_error}")
        
        return {
            "success": True,
            "message": "Job created successfully",
            "data": {"job_id": job.id}
        }
    except Exception as e:
        db.rollback()
        print(f"   ❌ ERROR creating job: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "message": f"Failed to create job: {str(e)}",
            "data": {}
        }

@router.get("/job/edit/{job_id}")
async def get_job_for_edit(job_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get job details for editing"""
    
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        return {
            "success": False,
            "message": "Job not found",
            "data": {}
        }
    
    # Verify ownership
    company = db.query(Company).filter(Company.id == job.company_id, Company.user_id == current_user.id).first()
    if not company:
        return {
            "success": False,
            "message": "Unauthorized",
            "data": {}
        }
    
    return {
        "success": True,
        "message": "Job details retrieved",
        "data": {
            "job": {
                "id": job.id,
                "company_id": job.company_id,
                "title": job.title,
                "description": job.description,
                "requirements": job.requirements,
                "responsibilities": job.responsibilities,
                "category_id": job.category_id,
                "job_type_id": job.job_type_id,
                "job_level_id": job.job_level_id,
                "salary_min": job.salary_min,
                "salary_max": job.salary_max,
                "location": job.location,
                "city_id": job.city_id,
                "deadline": str(job.deadline) if job.deadline else None,
                "vacancies": job.vacancies,
                "experience_required": job.experience_required,
                "is_active": job.is_active
            }
        }
    }

@router.post("/job/update")
async def update_job(data: JobUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Update job posting"""
    
    job = db.query(Job).filter(Job.id == data.id).first()
    if not job:
        return {
            "success": False,
            "message": "Job not found",
            "data": {}
        }
    
    # Verify ownership
    company = db.query(Company).filter(Company.id == job.company_id, Company.user_id == current_user.id).first()
    if not company:
        return {
            "success": False,
            "message": "Unauthorized",
            "data": {}
        }
    
    job.title = data.title
    job.description = data.description
    job.requirements = data.requirements
    job.responsibilities = data.responsibilities
    job.category_id = data.category_id
    job.job_type_id = data.job_type_id
    job.job_level_id = data.job_level_id
    job.salary_min = data.salary_min
    job.salary_max = data.salary_max
    job.location = data.location
    job.city_id = data.city_id
    job.deadline = data.deadline
    job.vacancies = data.vacancies
    job.experience_required = data.experience_required
    job.is_active = data.is_active
    
    db.commit()
    
    return {
        "success": True,
        "message": "Job updated successfully",
        "data": {}
    }

@router.delete("/job/delete/{job_id}")
async def delete_job(job_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Delete job posting"""
    
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        return {
            "success": False,
            "message": "Job not found",
            "data": {}
        }
    
    # Verify ownership
    company = db.query(Company).filter(Company.id == job.company_id, Company.user_id == current_user.id).first()
    if not company:
        return {
            "success": False,
            "message": "Unauthorized",
            "data": {}
        }
    
    db.delete(job)
    db.commit()
    
    return {
        "success": True,
        "message": "Job deleted successfully",
        "data": {}
    }
