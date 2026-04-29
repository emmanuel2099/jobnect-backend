from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta, datetime
from typing import Optional

from app.database import get_db
from app.models import User, Company, Resume
from app.schemas import UserRegister, UserLogin, StandardResponse
from app.auth import hash_password, verify_password, create_access_token, get_current_user
from app.config import settings

router = APIRouter()


def _normalize_user_type(raw_value: Optional[str]) -> str:
    value = (raw_value or "").strip().lower()
    if value in {"company", "employer", "recruiter"}:
        return "company"
    if value in {"applicant", "jobseeker", "job_seeker", "job-seeker", "candidate", "user"}:
        return "applicant"
    return ""

@router.post("/registration")
async def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """Register a new user (auto-login without OTP)"""
    try:
        print(f"📝 Registration request received for: {user_data.email}")
        
        # Validate password confirmation
        if user_data.password != user_data.password_confirmation:
            print("❌ Password mismatch")
            return {
                "success": False,
                "message": "Passwords do not match",
                "data": {}
            }
        
        # Check if email already exists
        print("🔍 Checking if email exists...")
        existing_user = db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            print("❌ Email already exists")
            return {
                "success": False,
                "message": "Validation errors",
                "data": {"email": ["The email has already been taken."]}
            }
        
        # Check if phone already exists
        print("🔍 Checking if phone exists...")
        existing_phone = db.query(User).filter(User.phone == user_data.phone).first()
        if existing_phone:
            print("❌ Phone already exists")
            return {
                "success": False,
                "message": "Validation errors",
                "data": {"phone": ["The phone has already been taken."]}
            }
        
        # Hash password
        print("🔐 Hashing password...")
        hashed_pwd = hash_password(user_data.password)
        print(f"✅ Password hashed (length: {len(hashed_pwd)})")
        
        # Determine user type using explicit type first, then fallback to legacy company field.
        requested_user_type = _normalize_user_type(user_data.user_type) or _normalize_user_type(user_data.account_type)
        if requested_user_type:
            user_type = requested_user_type
        elif not user_data.company or user_data.company.strip() in {"", "N/A"}:
            user_type = "applicant"
        else:
            user_type = "company"
            
        print(f"🔍 Debug: determined user_type: {user_type}")
        
        # Get company logo from request body if provided
        company_logo = None
        if hasattr(user_data, 'company_logo') and user_data.company_logo:
            company_logo = user_data.company_logo
        
        # Create new user
        print(f"👤 Creating new user with type: {user_type}...")
        new_user = User(
            name=user_data.name,
            email=user_data.email,
            phone=user_data.phone,
            password=hashed_pwd,
            company=user_data.company or "N/A",
            company_logo=company_logo,
            user_type=user_type,
            is_active=True,
            is_online=True,
            last_login=datetime.utcnow()
        )
        
        print("💾 Saving to database...")
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        print(f"✅ User created with ID: {new_user.id}")

        # Keep profile data separated by flow:
        # - applicants get a Resume row
        # - companies get a Company row
        if user_type == "company":
            existing_company = db.query(Company).filter(Company.user_id == new_user.id).first()
            if not existing_company:
                db.add(Company(
                    user_id=new_user.id,
                    name=(user_data.company or user_data.name).strip(),
                    logo=company_logo,
                    email=new_user.email,
                    phone=new_user.phone,
                    is_active=True
                ))
                db.commit()
        else:
            existing_resume = db.query(Resume).filter(Resume.user_id == new_user.id).first()
            if not existing_resume:
                db.add(Resume(user_id=new_user.id))
                db.commit()
        
        # Generate access token for immediate login (OTP will be post-registration KYC)
        print("🔑 Generating access token for immediate login...")
        access_token = create_access_token(
            data={"sub": new_user.email, "user_id": new_user.id}
        )
        
        response = {
            "success": True,
            "message": "Registration successful - Welcome to Eagle's Pride!",
            "data": {
                "token": access_token,
                "token_type": "bearer",
                "user": {
                    "id": new_user.id,
                    "name": new_user.name,
                    "email": new_user.email,
                    "phone": new_user.phone,
                    "company": new_user.company,
                    "companyLogo": new_user.company_logo,
                    "userType": new_user.user_type,
                    "profilePhoto": new_user.profile_photo,
                    "email_verified": False,  # KYC pending
                    "kyc_required": True  # User must complete KYC
                },
                "kyc_message": "Please complete email verification to access all features"
            }
        }
        print("✅ Registration successful with immediate login, KYC pending")
        return response
        
    except Exception as e:
        print(f"❌ ERROR in registration: {str(e)}")
        print(f"❌ Error type: {type(e).__name__}")
        import traceback
        print(f"❌ Traceback: {traceback.format_exc()}")
        db.rollback()
        return {
            "success": False,
            "message": f"Registration failed: {str(e)}",
            "data": {}
        }

@router.post("/registration-verification")
async def verify_registration(data: dict, db: Session = Depends(get_db)):
    """OTP verification endpoint (not used, kept for compatibility)"""
    return {
        "success": True,
        "message": "Verification successful",
        "data": {}
    }

@router.post("/login")
async def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """User login"""
    try:
        print(f"🔐 Login attempt for: {credentials.email}")
        
        # Find user by email
        user = db.query(User).filter(User.email == credentials.email).first()
        print(f"👤 User found: {user is not None}")
        print(f"👤 User found: {user is not None}")
    
        if not user or not verify_password(credentials.password, user.password):
            print("❌ Invalid credentials")
            return {
                "success": False,
                "message": "Invalid credentials",
                "data": {}
            }
        
        if not user.is_active:
            print("❌ Account inactive")
            return {
                "success": False,
                "message": "Account is inactive",
                "data": {}
            }
        
        # Update login status
        print("✅ Updating login status...")
        user.is_online = True
        user.last_login = datetime.utcnow()
        db.commit()
        
        # Generate token
        print("🔑 Generating token...")
        access_token = create_access_token(
            data={"sub": user.email, "user_id": user.id}
        )
        
        print("✅ Login successful")
        print(f"🔍 Debug: Login user_type: '{user.user_type}'")
        print(f"🔍 Debug: Login company: '{user.company}'")
        return {
            "success": True,
            "message": "Login successful",
            "data": {
                "token": access_token,
                "token_type": "bearer",
                "user": {
                    "id": user.id,
                    "name": user.name,
                    "email": user.email,
                    "phone": user.phone,
                    "company": user.company,
                    "companyLogo": user.company_logo,
                    "userType": user.user_type,
                    "profilePhoto": user.profile_photo
                }
            }
        }
    except Exception as e:
        print(f"❌ Login error: {str(e)}")
        import traceback
        print(f"❌ Traceback: {traceback.format_exc()}")
        db.rollback()
        return {
            "success": False,
            "message": f"Login failed: {str(e)}",
            "data": {}
        }

@router.post("/password-reset-email-verification")
async def send_password_reset_otp(data: dict, db: Session = Depends(get_db)):
    """Send password reset OTP"""
    email = data.get("email")
    
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return {
            "success": False,
            "message": "Email not found",
            "data": {}
        }
    
    # Generate a simple OTP (in production, send via email)
    import random
    otp = str(random.randint(100000, 999999))
    
    # Store OTP in session or cache (simplified for now)
    # In production, use Redis or database with expiry
    
    return {
        "success": True,
        "message": "OTP sent to email",
        "data": {"otp": otp}  # Remove this in production
    }

@router.post("/reset-password")
async def reset_password(data: dict, db: Session = Depends(get_db)):
    """Reset password with OTP"""
    email = data.get("email")
    new_password = data.get("password")
    otp = data.get("otp")
    
    # In production, verify OTP here
    
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return {
            "success": False,
            "message": "User not found",
            "data": {}
        }
    
    user.password = hash_password(new_password)
    db.commit()
    
    return {
        "success": True,
        "message": "Password reset successful",
        "data": {}
    }

@router.post("/change-password")
async def change_password(
    data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Change password for logged-in user"""
    old_password = data.get("old_password")
    new_password = data.get("new_password")
    
    if not old_password or not new_password:
        return {
            "success": False,
            "message": "Old password and new password are required",
            "data": {}
        }
    
    # Verify old password
    if not verify_password(old_password, current_user.password):
        return {
            "success": False,
            "message": "Old password is incorrect",
            "data": {}
        }
    
    # Update password
    current_user.password = hash_password(new_password)
    db.commit()
    
    return {
        "success": True,
        "message": "Password changed successfully",
        "data": {}
    }

@router.put("/update-profile")
async def update_profile(
    data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user profile"""
    
    # Update allowed fields
    if "name" in data:
        current_user.name = data["name"]
    if "phone" in data:
        # Check if phone is already taken by another user
        existing = db.query(User).filter(
            User.phone == data["phone"],
            User.id != current_user.id
        ).first()
        if existing:
            return {
                "success": False,
                "message": "Phone number already in use",
                "data": {}
            }
        current_user.phone = data["phone"]
    if "company" in data:
        current_user.company = data["company"]
    if "profile_photo" in data:
        current_user.profile_photo = data["profile_photo"]
    if "company_logo" in data:
        current_user.company_logo = data["company_logo"]
    if "date_of_birth" in data:
        # Store as string for simplicity
        pass  # Handle in resume table if needed
    if "designation_id" in data:
        # Store designation_id if needed
        pass  # Handle in resume table if needed
    if "gender" in data:
        # Store gender if needed
        pass  # Handle in resume table if needed
    
    current_user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(current_user)
    
    return {
        "success": True,
        "message": "Profile updated successfully",
        "data": {
            "user": {
                "id": current_user.id,
                "name": current_user.name,
                "email": current_user.email,
                "phone": current_user.phone,
                "company": current_user.company,
                "companyLogo": current_user.company_logo,
                "userType": current_user.user_type,
                "profilePhoto": current_user.profile_photo
            }
        }
    }

@router.get("/users/list")
async def list_users(db: Session = Depends(get_db)):
    """List all users (for testing/admin purposes)"""
    users = db.query(User).all()
    
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
                    "companyLogo": user.company_logo,
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

@router.post("/logout")
async def logout(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """User logout - update online status"""
    current_user.is_online = False
    db.commit()
    
    return {
        "success": True,
        "message": "Logged out successfully",
        "data": {}
    }

@router.get("/validate-session")
async def validate_session(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Validate if user session is still valid"""
    try:
        # Check if user still exists in database (not deleted)
        user = db.query(User).filter(User.id == current_user.id).first()
        
        if not user:
            # User has been deleted - session is invalid
            return {
                "success": False,
                "message": "Session invalid - user not found",
                "data": {"valid": False}
            }
        
        # Session is valid
        return {
            "success": True,
            "message": "Session is valid",
            "data": {
                "valid": True,
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "name": user.name,
                    "user_type": user.user_type
                }
            }
        }
        
    except Exception as e:
        print(f"❌ Error validating session: {e}")
        return {
            "success": False,
            "message": "Session validation failed",
            "data": {"valid": False}
        }
