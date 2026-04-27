from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from ..database import get_db
from ..email_service import email_service
from ..auth import get_current_user

router = APIRouter(prefix="/email", tags=["Email Verification"])

class SendVerificationRequest(BaseModel):
    email: EmailStr
    name: str = "User"

class VerifyEmailRequest(BaseModel):
    email: EmailStr
    otp: str

class ResendVerificationRequest(BaseModel):
    email: EmailStr

@router.post("/setup-database")
async def setup_email_database(db: Session = Depends(get_db)):
    """Setup email_otps table if it doesn't exist"""
    try:
        from sqlalchemy import text
        
        # Check if table exists
        result = db.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_name = 'email_otps'
        """)).fetchone()
        
        if result:
            return {
                "success": True,
                "message": "email_otps table already exists"
            }
        
        # Create the table (PostgreSQL compatible)
        db.execute(text("""
            CREATE TABLE email_otps (
                id SERIAL PRIMARY KEY,
                email VARCHAR(255) NOT NULL,
                otp VARCHAR(10) NOT NULL,
                purpose VARCHAR(50) DEFAULT 'email_verification',
                expires_at TIMESTAMP NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))
        
        # Create indexes separately
        db.execute(text("CREATE INDEX idx_email_purpose ON email_otps (email, purpose)"))
        db.execute(text("CREATE INDEX idx_expires_at ON email_otps (expires_at)"))
        
        db.commit()
        
        return {
            "success": True,
            "message": "email_otps table created successfully"
        }
        
    except Exception as e:
        db.rollback()
        return {
            "success": False,
            "message": f"Failed to create email_otps table: {str(e)}"
        }

@router.post("/send-verification")
async def send_verification_email(request: SendVerificationRequest, db: Session = Depends(get_db)):
    """Send email verification OTP"""
    try:
        # Send verification email (don't check if user exists yet)
        result = email_service.send_verification_email(
            email=request.email,
            name=request.name
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send verification email: {str(e)}")

@router.post("/verify")
async def verify_email(request: VerifyEmailRequest, db: Session = Depends(get_db)):
    """Verify email with OTP code"""
    try:
        # Verify the OTP
        result = email_service.verify_email_otp(
            email=request.email,
            otp=request.otp
        )
        
        if result["success"]:
            # Try to update user's email verification status if user exists
            try:
                from sqlalchemy import text
                db.execute(
                    text("UPDATE users SET email_verified = 1, updated_at = CURRENT_TIMESTAMP WHERE email = :email"),
                    {"email": request.email}
                )
                db.commit()
            except:
                # User might not exist yet, that's okay for testing
                pass
            
            return {
                "success": True,
                "message": "Email verified successfully"
            }
        else:
            return result
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Email verification failed: {str(e)}")

@router.post("/resend-verification")
async def resend_verification_email(request: ResendVerificationRequest, db: Session = Depends(get_db)):
    """Resend email verification OTP"""
    try:
        # Check if user exists
        from sqlalchemy import text
        user = db.execute(
            text("SELECT id, name, email_verified FROM users WHERE email = :email"),
            {"email": request.email}
        ).fetchone()
        
        if not user:
            return {
                "success": False,
                "message": "Email not found"
            }
        
        if user[2]:  # email_verified = True
            return {
                "success": False,
                "message": "Email is already verified"
            }
        
        # Send verification email
        result = email_service.send_verification_email(
            email=request.email,
            name=user[1] or "User"
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to resend verification email: {str(e)}")

@router.post("/send-password-reset")
async def send_password_reset_email(request: SendVerificationRequest, db: Session = Depends(get_db)):
    """Send password reset OTP"""
    try:
        # Check if user exists
        from sqlalchemy import text
        user = db.execute(
            text("SELECT id, name FROM users WHERE email = :email"),
            {"email": request.email}
        ).fetchone()
        
        if not user:
            return {
                "success": False,
                "message": "Email not found"
            }
        
        # Send password reset email
        result = email_service.send_password_reset_email(
            email=request.email,
            name=user[1] or "User"
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send password reset email: {str(e)}")

@router.post("/verify-password-reset")
async def verify_password_reset(request: VerifyEmailRequest, db: Session = Depends(get_db)):
    """Verify password reset OTP"""
    try:
        # Verify the OTP for password reset
        result = email_service.verify_email_otp(request.email, request.otp)
        
        if result["success"]:
            # Generate a temporary reset token (you can implement this)
            return {
                "success": True,
                "message": "Password reset code verified",
                "reset_token": "temp_token_here"  # Implement proper token generation
            }
        else:
            return result
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Password reset verification failed: {str(e)}")

@router.get("/verification-status")
async def get_verification_status(email: str, db: Session = Depends(get_db)):
    """Check email verification status"""
    try:
        from sqlalchemy import text
        user = db.execute(
            text("SELECT email_verified FROM users WHERE email = :email"),
            {"email": email}
        ).fetchone()
        
        if not user:
            return {
                "success": True,
                "email_verified": False,
                "message": "User not found - not verified"
            }
        
        return {
            "success": True,
            "email_verified": bool(user[0]),
            "message": "Verified" if user[0] else "Not verified"
        }
        
    except Exception as e:
        # If there's an error (like column doesn't exist), return default
        return {
            "success": True,
            "email_verified": False,
            "message": "Status unknown - database error"
        }