from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import JobSeeker, CompanyUser, Company
from app.schemas import (
    JobSeekerRegister, JobSeekerLogin, JobSeekerResponse,
    CompanyUserRegister, CompanyUserLogin, CompanyUserResponse,
    Token, UserLogin
)
from app.auth import hash_password, verify_password, create_access_token
from datetime import datetime

router = APIRouter()

# Job Seeker Authentication
@router.post("/job-seeker/register", status_code=status.HTTP_201_CREATED)
async def job_seeker_register(job_seeker_data: JobSeekerRegister, db: Session = Depends(get_db)):
    """Register a new job seeker"""
    print("Received job seeker registration request")
    
    # Check if job seeker already exists
    if db.query(JobSeeker).filter(JobSeeker.email == job_seeker_data.email).first():
        print(f"Job seeker with email {job_seeker_data.email} already exists")
        return {
            "success": False,
            "message": "Validation errors",
            "data": {"email": ["The email has already been taken."]}
        }
        
    if db.query(JobSeeker).filter(JobSeeker.phone == job_seeker_data.phone).first():
        print(f"Job seeker with phone {job_seeker_data.phone} already exists")
        return {
            "success": False,
            "message": "Validation errors",
            "data": {"phone": ["The phone has already been taken."]}
        }
        
    # Hash password
    print("🔐 Hashing password...")
    hashed_pwd = hash_password(job_seeker_data.password)
    print(f"✅ Password hashed (length: {len(hashed_pwd)})")
    
    # Create new job seeker
    print(f"👤 Creating new job seeker...")
    new_job_seeker = JobSeeker(
        name=job_seeker_data.name,
        email=job_seeker_data.email,
        phone=job_seeker_data.phone,
        password=hashed_pwd,
        is_active=True,
        is_online=True,
        last_login=datetime.utcnow()
    )
    
    print("💾 Saving to database...")
    db.add(new_job_seeker)
    db.commit()
    db.refresh(new_job_seeker)
    print(f"✅ Job seeker created with ID: {new_job_seeker.id}")
    
    # Generate access token for immediate login
    print("🔑 Generating access token for immediate login...")
    access_token = create_access_token(
        data={"sub": new_job_seeker.email, "user_id": new_job_seeker.id, "user_type": "applicant"}
    )
    
    response = {
        "success": True,
        "message": "Job seeker registration successful - Welcome to JobNect!",
        "data": {
            "token": access_token,
            "token_type": "bearer",
            "user": {
                "id": new_job_seeker.id,
                "name": new_job_seeker.name,
                "email": new_job_seeker.email,
                "phone": new_job_seeker.phone,
                "profilePhoto": new_job_seeker.profile_photo,
                "userType": "applicant",
                "email_verified": False,
                "kyc_required": True
            }
        }
    }
    
    return response

@router.post("/job-seeker/login")
async def job_seeker_login(login_data: JobSeekerLogin, db: Session = Depends(get_db)):
    """Login job seeker"""
    print(f"🔍 Job seeker login attempt: {login_data.email}")
    
    # Find job seeker by email
    job_seeker = db.query(JobSeeker).filter(JobSeeker.email == login_data.email).first()
    
    if not job_seeker or not verify_password(login_data.password, job_seeker.password):
        print("❌ Invalid credentials for job seeker")
        return {
            "success": False,
            "message": "Invalid credentials",
            "data": {}
        }
    
    if not job_seeker.is_active:
        print("❌ Job seeker account is deactivated")
        return {
            "success": False,
            "message": "Account is deactivated",
            "data": {}
        }
    
    # Update last login
    job_seeker.last_login = datetime.utcnow()
    job_seeker.is_online = True
    db.commit()
    
    print(f"✅ Job seeker login successful: {job_seeker.email}")
    
    # Generate access token
    access_token = create_access_token(
        data={"sub": job_seeker.email, "user_id": job_seeker.id, "user_type": "applicant"}
    )
    
    return {
        "success": True,
        "message": "Login successful",
        "data": {
            "token": access_token,
            "token_type": "bearer",
            "user": {
                "id": job_seeker.id,
                "name": job_seeker.name,
                "email": job_seeker.email,
                "phone": job_seeker.phone,
                "profilePhoto": job_seeker.profile_photo,
                "userType": "applicant",
                "is_online": job_seeker.is_online,
                "last_login": job_seeker.last_login.isoformat() if job_seeker.last_login else None
            }
        }
    }

# Company User Authentication
@router.post("/company/register", status_code=status.HTTP_201_CREATED)
async def company_user_register(company_user_data: CompanyUserRegister, db: Session = Depends(get_db)):
    """Register a new company user"""
    print("Received company user registration request")
    
    # Check if company user already exists
    if db.query(CompanyUser).filter(CompanyUser.email == company_user_data.email).first():
        print(f"Company user with email {company_user_data.email} already exists")
        return {
            "success": False,
            "message": "Validation errors",
            "data": {"email": ["The email has already been taken."]}
        }
        
    if db.query(CompanyUser).filter(CompanyUser.phone == company_user_data.phone).first():
        print(f"Company user with phone {company_user_data.phone} already exists")
        return {
            "success": False,
            "message": "Validation errors",
            "data": {"phone": ["The phone has already been taken."]}
        }
        
    # Hash password
    print("🔐 Hashing password...")
    hashed_pwd = hash_password(company_user_data.password)
    print(f"✅ Password hashed (length: {len(hashed_pwd)})")
    
    # Create new company user
    print(f"👤 Creating new company user...")
    new_company_user = CompanyUser(
        name=company_user_data.name,
        email=company_user_data.email,
        phone=company_user_data.phone,
        password=hashed_pwd,
        company_name=company_user_data.company_name,
        company_logo=company_user_data.company_logo,
        is_active=True,
        is_online=True,
        last_login=datetime.utcnow()
    )
    
    print("💾 Saving to database...")
    db.add(new_company_user)
    db.commit()
    db.refresh(new_company_user)
    print(f"✅ Company user created with ID: {new_company_user.id}")
    
    # Create associated company record
    print("🏢 Creating company record...")
    new_company = Company(
        company_user_id=new_company_user.id,
        name=company_user_data.company_name,
        logo=company_user_data.company_logo,
        email=company_user_data.email,
        phone=company_user_data.phone,
        is_active=True
    )
    
    db.add(new_company)
    db.commit()
    db.refresh(new_company)
    print(f"✅ Company record created with ID: {new_company.id}")
    
    # Generate access token for immediate login
    print("🔑 Generating access token for immediate login...")
    access_token = create_access_token(
        data={"sub": new_company_user.email, "user_id": new_company_user.id, "user_type": "company"}
    )
    
    response = {
        "success": True,
        "message": "Company registration successful - Welcome to JobNect!",
        "data": {
            "token": access_token,
            "token_type": "bearer",
            "user": {
                "id": new_company_user.id,
                "name": new_company_user.name,
                "email": new_company_user.email,
                "phone": new_company_user.phone,
                "company_name": new_company_user.company_name,
                "companyLogo": new_company_user.company_logo,
                "profilePhoto": new_company_user.profile_photo,
                "userType": "company",
                "company_id": new_company.id,
                "email_verified": False
            }
        }
    }
    
    return response

@router.post("/company/login")
async def company_user_login(login_data: CompanyUserLogin, db: Session = Depends(get_db)):
    """Login company user"""
    print(f"🔍 Company user login attempt: {login_data.email}")
    
    # Find company user by email
    company_user = db.query(CompanyUser).filter(CompanyUser.email == login_data.email).first()
    
    if not company_user or not verify_password(login_data.password, company_user.password):
        print("❌ Invalid credentials for company user")
        return {
            "success": False,
            "message": "Invalid credentials",
            "data": {}
        }
    
    if not company_user.is_active:
        print("❌ Company user account is deactivated")
        return {
            "success": False,
            "message": "Account is deactivated",
            "data": {}
        }
    
    # Update last login
    company_user.last_login = datetime.utcnow()
    company_user.is_online = True
    db.commit()
    
    print(f"✅ Company user login successful: {company_user.email}")
    
    # Generate access token
    access_token = create_access_token(
        data={"sub": company_user.email, "user_id": company_user.id, "user_type": "company"}
    )
    
    # Get associated company
    company = db.query(Company).filter(Company.company_user_id == company_user.id).first()
    
    return {
        "success": True,
        "message": "Login successful",
        "data": {
            "token": access_token,
            "token_type": "bearer",
            "user": {
                "id": company_user.id,
                "name": company_user.name,
                "email": company_user.email,
                "phone": company_user.phone,
                "company_name": company_user.company_name,
                "companyLogo": company_user.company_logo,
                "profilePhoto": company_user.profile_photo,
                "userType": "company",
                "company_id": company.id if company else None,
                "is_online": company_user.is_online,
                "last_login": company_user.last_login.isoformat() if company_user.last_login else None
            }
        }
    }

# Universal Login (tries both tables)
@router.post("/universal-login")
async def universal_login(login_data: UserLogin, db: Session = Depends(get_db)):
    """Universal login - tries both job seeker and company user tables"""
    print(f"🔍 Universal login attempt: {login_data.email}")
    
    # Try job seeker first
    job_seeker = db.query(JobSeeker).filter(JobSeeker.email == login_data.email).first()
    if job_seeker and verify_password(login_data.password, job_seeker.password):
        if not job_seeker.is_active:
            return {
                "success": False,
                "message": "Account is deactivated",
                "data": {}
            }
        
        # Update last login
        job_seeker.last_login = datetime.utcnow()
        job_seeker.is_online = True
        db.commit()
        
        print(f"✅ Job seeker login successful: {job_seeker.email}")
        
        access_token = create_access_token(
            data={"sub": job_seeker.email, "user_id": job_seeker.id, "user_type": "applicant"}
        )
        
        return {
            "success": True,
            "message": "Login successful",
            "data": {
                "token": access_token,
                "token_type": "bearer",
                "user": {
                    "id": job_seeker.id,
                    "name": job_seeker.name,
                    "email": job_seeker.email,
                    "phone": job_seeker.phone,
                    "profilePhoto": job_seeker.profile_photo,
                    "userType": "applicant",
                    "is_online": job_seeker.is_online,
                    "last_login": job_seeker.last_login.isoformat() if job_seeker.last_login else None
                }
            }
        }
    
    # Try company user
    company_user = db.query(CompanyUser).filter(CompanyUser.email == login_data.email).first()
    if company_user and verify_password(login_data.password, company_user.password):
        if not company_user.is_active:
            return {
                "success": False,
                "message": "Account is deactivated",
                "data": {}
            }
        
        # Update last login
        company_user.last_login = datetime.utcnow()
        company_user.is_online = True
        db.commit()
        
        print(f"✅ Company user login successful: {company_user.email}")
        
        access_token = create_access_token(
            data={"sub": company_user.email, "user_id": company_user.id, "user_type": "company"}
        )
        
        # Get associated company
        company = db.query(Company).filter(Company.company_user_id == company_user.id).first()
        
        return {
            "success": True,
            "message": "Login successful",
            "data": {
                "token": access_token,
                "token_type": "bearer",
                "user": {
                    "id": company_user.id,
                    "name": company_user.name,
                    "email": company_user.email,
                    "phone": company_user.phone,
                    "company_name": company_user.company_name,
                    "companyLogo": company_user.company_logo,
                    "profilePhoto": company_user.profile_photo,
                    "userType": "company",
                    "company_id": company.id if company else None,
                    "is_online": company_user.is_online,
                    "last_login": company_user.last_login.isoformat() if company_user.last_login else None
                }
            }
        }
    
    # If not found in either table
    print("❌ Invalid credentials - not found in either table")
    return {
        "success": False,
        "message": "Invalid credentials",
        "data": {}
    }
