from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta

from app.database import get_db
from app.models import User
from app.schemas import UserRegister, UserLogin, StandardResponse
from app.auth import hash_password, verify_password, create_access_token, get_current_user
from app.config import settings

router = APIRouter()

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
        
        # Create new user
        print("👤 Creating new user...")
        new_user = User(
            name=user_data.name,
            email=user_data.email,
            phone=user_data.phone,
            password=hashed_pwd,
            company=user_data.company or "N/A",
            user_type="applicant",
            is_active=True
        )
        
        print("💾 Saving to database...")
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        print(f"✅ User created with ID: {new_user.id}")
        
        # Auto-login: Generate token
        print("🔑 Generating access token...")
        access_token = create_access_token(
            data={"sub": new_user.email, "user_id": new_user.id}
        )
        print("✅ Token generated")
        
        response = {
            "success": True,
            "message": "Registration successful",
            "data": {
                "token": access_token,
                "token_type": "bearer",
                "user": {
                    "id": new_user.id,
                    "name": new_user.name,
                    "email": new_user.email,
                    "phone": new_user.phone,
                    "company": new_user.company,
                    "userType": new_user.user_type,
                    "profilePhoto": new_user.profile_photo
                }
            }
        }
        print("✅ Registration successful, returning response")
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
    
    # Find user by email
    user = db.query(User).filter(User.email == credentials.email).first()
    
    if not user or not verify_password(credentials.password, user.password):
        return {
            "success": False,
            "message": "Invalid credentials",
            "data": {}
        }
    
    if not user.is_active:
        return {
            "success": False,
            "message": "Account is inactive",
            "data": {}
        }
    
    # Generate token
    access_token = create_access_token(
        data={"sub": user.email, "user_id": user.id}
    )
    
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
                "userType": user.user_type,
                "profilePhoto": user.profile_photo
            }
        }
    }

@router.post("/password-reset-email-verification")
async def send_password_reset_otp(data: dict, db: Session = Depends(get_db)):
    """Send password reset OTP (placeholder)"""
    email = data.get("email")
    
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return {
            "success": False,
            "message": "Email not found",
            "data": {}
        }
    
    # In production, send actual OTP email here
    return {
        "success": True,
        "message": "OTP sent to email",
        "data": {"otp": "123456"}  # Mock OTP
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
                    "userType": user.user_type,
                    "isActive": user.is_active,
                    "createdAt": user.created_at.isoformat() if user.created_at else None
                }
                for user in users
            ]
        }
    }
