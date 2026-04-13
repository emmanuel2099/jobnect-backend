from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.database import get_db
from app.models import Company, Job, Notification, SocialLink, KYC, User
from app.schemas import SocialLinkCreate, SocialLinkUpdate, KYCSubmit
from app.auth import get_current_user

router = APIRouter()

@router.get("/companies")
async def get_companies(limit: int = Query(100, ge=1, le=200), db: Session = Depends(get_db)):
    """Get all companies - includes both Company table entries and users with company type"""
    
    # Get companies from Company table
    company_table_entries = db.query(Company).filter(Company.is_active == True).order_by(desc(Company.created_at)).all()
    
    # Get users who are companies
    company_users = db.query(User).filter(
        User.user_type == "company",
        User.is_active == True
    ).order_by(desc(User.created_at)).limit(limit).all()
    
    companies_data = []
    
    # Add companies from Company table
    for company in company_table_entries:
        job_count = db.query(Job).filter(Job.company_id == company.id, Job.is_active == True).count()
        
        companies_data.append({
            "id": company.id,
            "user_id": company.user_id,
            "name": company.name,
            "logo": company.logo,
            "location": company.location,
            "description": company.description,
            "website": company.website,
            "email": company.email,
            "phone": company.phone,
            "job_count": job_count,
            "source": "company_table"
        })
    
    # Add companies from User table (registered companies)
    for user in company_users:
        # Check if this user already has a company entry
        existing_company = db.query(Company).filter(Company.user_id == user.id).first()
        if not existing_company:
            companies_data.append({
                "id": user.id,
                "user_id": user.id,
                "name": user.company or user.name,
                "logo": user.company_logo or user.profile_photo,
                "location": None,
                "description": f"Company registered by {user.name}",
                "website": None,
                "email": user.email,
                "phone": user.phone,
                "job_count": 0,
                "source": "user_table"
            })
    
    return {
        "success": True,
        "message": "Companies retrieved",
        "data": {"companies": companies_data}
    }

@router.get("/featured-companies")
async def get_featured_companies(limit: int = Query(10, ge=1, le=50), db: Session = Depends(get_db)):
    """Get featured companies"""
    
    companies = db.query(Company).filter(
        Company.is_active == True,
        Company.is_featured == True
    ).order_by(desc(Company.created_at)).limit(limit).all()
    
    companies_data = []
    for company in companies:
        job_count = db.query(Job).filter(Job.company_id == company.id, Job.is_active == True).count()
        
        companies_data.append({
            "id": company.id,
            "name": company.name,
            "logo": company.logo,
            "location": company.location,
            "description": company.description,
            "job_count": job_count
        })
    
    return {
        "success": True,
        "message": "Featured companies retrieved",
        "data": {"companies": companies_data}
    }

@router.get("/company/details/{company_id}")
async def get_company_details(company_id: int, db: Session = Depends(get_db)):
    """Get detailed company information"""
    
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        return {
            "success": False,
            "message": "Company not found",
            "data": {}
        }
    
    job_count = db.query(Job).filter(Job.company_id == company.id, Job.is_active == True).count()
    
    return {
        "success": True,
        "message": "Company details retrieved",
        "data": {
            "company": {
                "id": company.id,
                "name": company.name,
                "logo": company.logo,
                "location": company.location,
                "description": company.description,
                "website": company.website,
                "email": company.email,
                "phone": company.phone,
                "founded_year": company.founded_year,
                "company_size": company.company_size,
                "industry": company.industry,
                "is_featured": company.is_featured,
                "job_count": job_count
            }
        }
    }

@router.get("/company/jobs/{company_id}")
async def get_company_jobs(company_id: int, db: Session = Depends(get_db)):
    """Get all jobs from a specific company"""
    
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        return {
            "success": False,
            "message": "Company not found",
            "data": {}
        }
    
    jobs = db.query(Job).filter(Job.company_id == company_id, Job.is_active == True).order_by(desc(Job.created_at)).all()
    
    jobs_data = [{
        "id": job.id,
        "title": job.title,
        "description": job.description,
        "salary_min": job.salary_min,
        "salary_max": job.salary_max,
        "location": job.location,
        "deadline": str(job.deadline) if job.deadline else None,
        "vacancies": job.vacancies,
        "created_at": str(job.created_at)
    } for job in jobs]
    
    return {
        "success": True,
        "message": "Company jobs retrieved",
        "data": {"jobs": jobs_data}
    }

@router.get("/company/follower/index")
async def get_company_followers(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get followers of company (placeholder)"""
    
    return {
        "success": True,
        "message": "Followers retrieved",
        "data": {"followers": []}
    }

@router.get("/company/following/index")
async def get_company_followings(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get companies user is following (placeholder)"""
    
    return {
        "success": True,
        "message": "Followings retrieved",
        "data": {"followings": []}
    }

@router.get("/company/payment/index")
async def get_company_payments(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get company payment history (placeholder)"""
    
    return {
        "success": True,
        "message": "Payments retrieved",
        "data": {"payments": []}
    }

@router.get("/notifications")
async def get_notifications(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get user notifications"""
    
    notifications = db.query(Notification).filter(
        Notification.user_id == current_user.id
    ).order_by(desc(Notification.created_at)).limit(50).all()
    
    notifications_data = [{
        "id": notif.id,
        "title": notif.title,
        "message": notif.message,
        "type": notif.notification_type,
        "is_read": notif.is_read,
        "created_at": str(notif.created_at)
    } for notif in notifications]
    
    return {
        "success": True,
        "message": "Notifications retrieved",
        "data": {"notifications": notifications_data}
    }

# Social Links
@router.get("/social-links/index")
async def get_social_links(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get user's social links"""
    
    social_links = db.query(SocialLink).filter(SocialLink.user_id == current_user.id).all()
    
    links_data = [{
        "id": link.id,
        "platform": link.platform,
        "url": link.url
    } for link in social_links]
    
    return {
        "success": True,
        "message": "Social links retrieved",
        "data": {"social_links": links_data}
    }

@router.post("/social-links/store")
async def create_social_link(data: SocialLinkCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Add a social link"""
    
    social_link = SocialLink(
        user_id=current_user.id,
        platform=data.platform,
        url=data.url
    )
    
    db.add(social_link)
    db.commit()
    db.refresh(social_link)
    
    return {
        "success": True,
        "message": "Social link added",
        "data": {"link_id": social_link.id}
    }

@router.get("/social-links/edit/{link_id}")
async def get_social_link_for_edit(link_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get social link for editing"""
    
    link = db.query(SocialLink).filter(SocialLink.id == link_id, SocialLink.user_id == current_user.id).first()
    if not link:
        return {
            "success": False,
            "message": "Social link not found",
            "data": {}
        }
    
    return {
        "success": True,
        "message": "Social link retrieved",
        "data": {
            "link": {
                "id": link.id,
                "platform": link.platform,
                "url": link.url
            }
        }
    }

@router.post("/social-links/update")
async def update_social_link(data: SocialLinkUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Update a social link"""
    
    link = db.query(SocialLink).filter(SocialLink.id == data.id, SocialLink.user_id == current_user.id).first()
    if not link:
        return {
            "success": False,
            "message": "Social link not found",
            "data": {}
        }
    
    link.platform = data.platform
    link.url = data.url
    db.commit()
    
    return {
        "success": True,
        "message": "Social link updated",
        "data": {}
    }

@router.delete("/social-links/delete/{link_id}")
async def delete_social_link(link_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Delete a social link"""
    
    link = db.query(SocialLink).filter(SocialLink.id == link_id, SocialLink.user_id == current_user.id).first()
    if not link:
        return {
            "success": False,
            "message": "Social link not found",
            "data": {}
        }
    
    db.delete(link)
    db.commit()
    
    return {
        "success": True,
        "message": "Social link deleted",
        "data": {}
    }

# KYC
@router.post("/applicant/kyc/store")
async def submit_kyc(data: KYCSubmit, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Submit KYC verification"""
    
    # Check if KYC already exists
    existing_kyc = db.query(KYC).filter(KYC.user_id == current_user.id).first()
    
    if existing_kyc:
        # Update existing KYC
        existing_kyc.first_name = data.first_name
        existing_kyc.last_name = data.last_name
        existing_kyc.document_type = data.document_type
        existing_kyc.document_number = data.document_number
        existing_kyc.document_file = data.document_file
        existing_kyc.status = "pending"
        db.commit()
    else:
        # Create new KYC
        kyc = KYC(
            user_id=current_user.id,
            first_name=data.first_name,
            last_name=data.last_name,
            document_type=data.document_type,
            document_number=data.document_number,
            document_file=data.document_file,
            status="pending"
        )
        db.add(kyc)
        db.commit()
    
    return {
        "success": True,
        "message": "KYC submitted successfully",
        "data": {"status": "pending"}
    }

@router.get("/applicant/kyc/get/status")
async def get_kyc_status(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get KYC verification status"""
    
    kyc = db.query(KYC).filter(KYC.user_id == current_user.id).first()
    
    if not kyc:
        return {
            "success": True,
            "message": "No KYC found",
            "data": {"status": "not_submitted"}
        }
    
    return {
        "success": True,
        "message": "KYC status retrieved",
        "data": {
            "status": kyc.status,
            "first_name": kyc.first_name,
            "last_name": kyc.last_name,
            "document_type": kyc.document_type,
            "submitted_at": str(kyc.created_at)
        }
    }
