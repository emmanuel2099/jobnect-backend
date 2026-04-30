from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.database import get_db
from app.models import JobApplication, Bookmark, Job, Company, User, Resume, Experience, Education, JobType
from app.schemas import JobApplicationCreate, BookmarkCreate
from app.auth import get_current_user
from app.notification_service import notify_job_application, notify_application_status_change

router = APIRouter()

@router.post("/applicant/job-apply")
async def apply_for_job(data: JobApplicationCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Apply for a job"""
    
    try:
        print(f"📝 Job application request - User: {current_user.id}, Job: {data.job_id}")
        
        # Check subscription before allowing application
        from app.subscription_service import SubscriptionService
        
        access_check = SubscriptionService.can_apply_to_job(db, current_user.id, data.job_id)
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
        
        # Send notification to company
        try:
            notify_job_application(db, data.job_id, current_user.id)
            print(f"📬 Notification sent to company")
        except Exception as notif_error:
            print(f"⚠️  Failed to send notification: {notif_error}")
        
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
    
    # Check if current_user is a JobSeeker or legacy User
    from app.models import JobSeeker
    is_job_seeker = isinstance(current_user, JobSeeker)
    
    # Query based on user type
    if is_job_seeker:
        applications = db.query(JobApplication).filter(
            JobApplication.job_seeker_id == current_user.id
        ).order_by(desc(JobApplication.created_at)).all()
    else:
        applications = db.query(JobApplication).filter(
            JobApplication.user_id == current_user.id
        ).order_by(desc(JobApplication.created_at)).all()
    
    applied_jobs = []
    for app in applications:
        job = db.query(Job).filter(Job.id == app.job_id).first()
        if job:
            company = db.query(Company).filter(Company.id == job.company_id).first()
            job_type = db.query(JobType).filter(JobType.id == job.job_type_id).first() if job.job_type_id else None
            
            applied_jobs.append({
                "id": app.id,
                "application_id": app.id,
                "status": app.status,
                "created_at": str(app.created_at),
                "applied_at": str(app.created_at),
                "job": {
                    "id": job.id,
                    "title": job.title,
                    "description": job.description,
                    "salary_min": job.salary_min,
                    "salary_max": job.salary_max,
                    "location": job.location,
                    "deadline": str(job.deadline) if job.deadline else None,
                    "job_type": {
                        "id": job_type.id,
                        "name": job_type.name
                    } if job_type else {"id": 1, "name": "FULL-TIME"},
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
    
    print(f"\n🔖 Fetching bookmarks for user {current_user.id}")
    
    bookmarks = db.query(Bookmark).filter(
        Bookmark.user_id == current_user.id
    ).order_by(desc(Bookmark.created_at)).all()
    
    print(f"   Found {len(bookmarks)} bookmarks")
    
    bookmarked_jobs = []
    for bookmark in bookmarks:
        job = db.query(Job).filter(Job.id == bookmark.job_id).first()
        if job:
            company = db.query(Company).filter(Company.id == job.company_id).first()
            
            print(f"   - Bookmark {bookmark.id}: Job {job.id} ({job.title})")
            
            bookmarked_jobs.append({
                "id": bookmark.id,
                "created_at": str(bookmark.created_at),
                "job": {
                    "id": job.id,
                    "title": job.title,
                    "description": job.description,
                    "salary_min": job.salary_min,
                    "salary_max": job.salary_max,
                    "currency": job.currency if hasattr(job, 'currency') else "USD",
                    "location": job.location,
                    "city": job.city if hasattr(job, 'city') else None,
                    "deadline": str(job.deadline) if job.deadline else None,
                    "created_at": str(job.created_at) if hasattr(job, 'created_at') else None,
                    "company": {
                        "id": company.id,
                        "name": company.name,
                        "logo": company.logo
                    } if company else None
                }
            })
    
    print(f"   ✅ Returning {len(bookmarked_jobs)} bookmarked jobs\n")
    
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
    
    print(f"\n🔍 DEBUG RECENT: Fetching recent applications for user {current_user.id}")
    
    # Find company owned by current user
    company = db.query(Company).filter(Company.user_id == current_user.id).first()
    if not company:
        print(f"   ❌ No company found for user {current_user.id}")
        return {
            "success": True,
            "message": "No company found",
            "data": {"applications": []}
        }
    
    print(f"   ✅ Company found: {company.id} ({company.name})")
    
    # Get all jobs for this company
    company_jobs = db.query(Job).filter(Job.company_id == company.id).all()
    job_ids = [job.id for job in company_jobs]
    
    print(f"   📋 Company has {len(company_jobs)} jobs: {job_ids}")
    
    # Get recent applications for these jobs (all of them, not limited)
    applications = db.query(JobApplication).filter(
        JobApplication.job_id.in_(job_ids)
    ).order_by(desc(JobApplication.created_at)).all()
    
    print(f"   📝 Found {len(applications)} applications")
    
    applications_data = []
    for app in applications:
        job = db.query(Job).filter(Job.id == app.job_id).first()
        applicant = db.query(User).filter(User.id == app.user_id).first()
        
        if job and applicant:
            print(f"      - App {app.id}: {applicant.name} → {job.title}")
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
    
    print(f"   ✅ Returning {len(applications_data)} applications\n")
    
    return {
        "success": True,
        "message": "Recent applications retrieved",
        "data": {"applications": applications_data}
    }

@router.get("/company/applications/by-job")
async def get_company_applications_by_job(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get applications grouped by job for company"""
    
    try:
        print(f"\n🔍 DEBUG: Fetching applications for user {current_user.id} ({current_user.name})")
        print(f"   User type: {current_user.user_type}")
        
        # Find company owned by current user
        company = db.query(Company).filter(Company.user_id == current_user.id).first()
        
        if company:
            print(f"   ✅ Company found: ID={company.id}, Name={company.name}")
        else:
            print(f"   ⚠️  No company record found for user {current_user.id}")
        
        # If no company record exists, check if user is a company type and get jobs directly
        if not company:
            # Check if user is company type
            if current_user.user_type != "company":
                print(f"   ❌ User is not a company type")
                return {
                    "success": True,
                    "message": "User is not a company",
                    "data": {"jobs": []}
                }
            
            # For company users without a Company record, return empty for now
            print(f"   ⚠️  Company user but no Company record exists")
            return {
                "success": True,
                "message": "No company profile found. Please complete your company profile.",
                "data": {"jobs": []}
            }
        
        # Get all jobs for this company
        jobs = db.query(Job).filter(Job.company_id == company.id).order_by(desc(Job.created_at)).all()
        print(f"   📋 Found {len(jobs)} jobs for company {company.id}")
        
        jobs_data = []
        for job in jobs:
            # Get applications for this job
            applications = db.query(JobApplication).filter(
                JobApplication.job_id == job.id
            ).order_by(desc(JobApplication.created_at)).all()
            
            print(f"      Job {job.id} ({job.title}): {len(applications)} applications")
            
            applications_list = []
            for app in applications:
                applicant = db.query(User).filter(User.id == app.user_id).first()
                if applicant:
                    print(f"         - Application {app.id} from {applicant.name} ({applicant.email})")
                    # Handle different profile picture field names
                    profile_pic = getattr(applicant, 'profile_picture', None) or getattr(applicant, 'profile_photo', None)
                    
                    applications_list.append({
                        "id": app.id,
                        "status": app.status,
                        "created_at": str(app.created_at),
                        "cover_letter": app.cover_letter,
                        "applicant": {
                            "id": applicant.id,
                            "name": applicant.name,
                            "email": applicant.email,
                            "phone": applicant.phone if hasattr(applicant, 'phone') else None,
                            "profile_picture": profile_pic
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
        
        print(f"   ✅ Returning {len(jobs_data)} jobs with applications\n")
        
        return {
            "success": True,
            "message": "Applications by job retrieved",
            "data": {"jobs": jobs_data}
        }
    except Exception as e:
        print(f"   ❌ ERROR in get_company_applications_by_job: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "message": f"Internal server error: {str(e)}",
            "data": {"jobs": []}
        }

@router.get("/company/applicant/{applicant_id}")
async def get_applicant_profile(applicant_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get full profile of an applicant including resume, skills, experience, education"""
    
    try:
        # Verify current user is a company
        if current_user.user_type != "company":
            return {
                "success": False,
                "message": "Unauthorized - Only companies can view applicant profiles",
                "data": {}
            }
        
        # Get applicant user
        applicant = db.query(User).filter(User.id == applicant_id).first()
        if not applicant:
            return {
                "success": False,
                "message": "Applicant not found",
                "data": {}
            }
        
        # Get resume
        resume = db.query(Resume).filter(Resume.user_id == applicant_id).first()
        
        # Get experiences
        experiences = []
        if resume:
            exps = db.query(Experience).filter(Experience.resume_id == resume.id).all()
            experiences = [{
                "id": exp.id,
                "business": exp.business,
                "employer": exp.employer,
                "designation": exp.designation,
                "department": exp.department,
                "responsibilities": exp.responsibilities,
                "start_date": str(exp.start_date) if exp.start_date else None,
                "end_date": str(exp.end_date) if exp.end_date else None
            } for exp in exps]
        
        # Get educations
        educations = []
        if resume:
            edus = db.query(Education).filter(Education.resume_id == resume.id).all()
            educations = [{
                "id": edu.id,
                "level": edu.level,
                "degree": edu.degree,
                "institution": edu.institution,
                "result": edu.result,
                "passing_year": edu.passing_year,
                "start_date": str(edu.start_date) if edu.start_date else None,
                "end_date": str(edu.end_date) if edu.end_date else None
            } for edu in edus]
        
        # Parse skills
        skills = []
        if resume and resume.skills:
            import json
            try:
                skills = json.loads(resume.skills)
            except:
                skills = []
        
        profile_data = {
            "id": applicant.id,
            "name": applicant.name,
            "email": applicant.email,
            "phone": applicant.phone,
            "profile_photo": getattr(applicant, 'profile_photo', None),
            "resume": {
                "designation": resume.designation if resume else None,
                "city": resume.city if resume else None,
                "objective": resume.objective if resume else None,
                "present_salary": resume.present_salary if resume else None,
                "expected_salary": resume.expected_salary if resume else None,
                "job_level": resume.job_level if resume else None,
                "job_nature": resume.job_nature if resume else None,
                "skills": skills
            } if resume else None,
            "experiences": experiences,
            "educations": educations
        }
        
        return {
            "success": True,
            "message": "Applicant profile retrieved",
            "data": profile_data
        }
    except Exception as e:
        print(f"❌ ERROR getting applicant profile: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "message": f"Failed to get applicant profile: {str(e)}",
            "data": {}
        }

@router.post("/company/application/approve")
async def approve_application(data: dict, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Approve a job application"""
    
    try:
        application_id = data.get('application_id')
        
        if not application_id:
            return {
                "success": False,
                "message": "Application ID is required",
                "data": {}
            }
        
        # Verify current user is a company
        if current_user.user_type != "company":
            return {
                "success": False,
                "message": "Unauthorized - Only companies can approve applications",
                "data": {}
            }
        
        # Get application
        application = db.query(JobApplication).filter(JobApplication.id == application_id).first()
        if not application:
            return {
                "success": False,
                "message": "Application not found",
                "data": {}
            }
        
        # Verify the job belongs to this company
        job = db.query(Job).filter(Job.id == application.job_id).first()
        company = db.query(Company).filter(Company.user_id == current_user.id).first()
        
        if not job or not company or job.company_id != company.id:
            return {
                "success": False,
                "message": "Unauthorized - This application does not belong to your company",
                "data": {}
            }
        
        # Update application status
        application.status = "approved"
        db.commit()
        
        print(f"✅ Application {application_id} approved by company {company.id}")
        
        # Send notification to applicant
        try:
            notify_application_status_change(db, application_id, "approved")
            print(f"📬 Approval notification sent to applicant {application.user_id}")
        except Exception as notif_error:
            print(f"⚠️  Failed to send approval notification: {notif_error}")
        
        # Get applicant user ID for conversation creation
        applicant = db.query(User).filter(User.id == application.user_id).first()
        
        return {
            "success": True,
            "message": "Application approved successfully",
            "data": {
                "application_id": application_id,
                "status": "approved",
                "applicant_user_id": applicant.id if applicant else None,
                "company_user_id": current_user.id
            }
        }
    except Exception as e:
        db.rollback()
        print(f"❌ ERROR approving application: {str(e)}")
        return {
            "success": False,
            "message": f"Failed to approve application: {str(e)}",
            "data": {}
        }

@router.get("/application/{application_id}/chat-info")
async def get_application_chat_info(application_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get user IDs for creating a conversation from an application"""
    
    try:
        # Get application
        application = db.query(JobApplication).filter(JobApplication.id == application_id).first()
        if not application:
            return {
                "success": False,
                "message": "Application not found",
                "data": {}
            }
        
        # Get job and company
        job = db.query(Job).filter(Job.id == application.job_id).first()
        if not job:
            return {
                "success": False,
                "message": "Job not found",
                "data": {}
            }
        
        company = db.query(Company).filter(Company.id == job.company_id).first()
        if not company:
            return {
                "success": False,
                "message": "Company not found",
                "data": {}
            }
        
        # Get company user
        company_user = db.query(User).filter(User.id == company.user_id).first()
        applicant_user = db.query(User).filter(User.id == application.user_id).first()
        
        if not company_user or not applicant_user:
            return {
                "success": False,
                "message": "User information not found",
                "data": {}
            }
        
        # Verify current user is either the applicant or company
        if current_user.id != applicant_user.id and current_user.id != company_user.id:
            return {
                "success": False,
                "message": "Unauthorized",
                "data": {}
            }
        
        # Determine the other user
        other_user_id = company_user.id if current_user.id == applicant_user.id else applicant_user.id
        other_user_name = company_user.name if current_user.id == applicant_user.id else applicant_user.name
        
        return {
            "success": True,
            "message": "Chat info retrieved",
            "data": {
                "application_id": application_id,
                "status": application.status,
                "applicant_user_id": applicant_user.id,
                "company_user_id": company_user.id,
                "other_user_id": other_user_id,
                "other_user_name": other_user_name,
                "company_name": company.name
            }
        }
    except Exception as e:
        print(f"❌ ERROR getting chat info: {str(e)}")
        return {
            "success": False,
            "message": f"Failed to get chat info: {str(e)}",
            "data": {}
        }

