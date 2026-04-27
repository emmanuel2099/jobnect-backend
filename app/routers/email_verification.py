from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from ..database import get_db
from ..email_service import email_service
from ..auth import get_current_user
import bcrypt

router = APIRouter(prefix="/email", tags=["Email Verification"])

class SendVerificationRequest(BaseModel):
    email: EmailStr
    name: str = "User"

class VerifyEmailRequest(BaseModel):
    email: EmailStr
    otp: str

class ResendVerificationRequest(BaseModel):
    email: EmailStr

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    email: EmailStr
    otp: str
    new_password: str
    confirm_password: str

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str
    confirm_password: str

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

@router.post("/forgot-password")
async def forgot_password(request: ForgotPasswordRequest, db: Session = Depends(get_db)):
    """Send forgot password OTP"""
    try:
        # Check if user exists
        from sqlalchemy import text
        user = db.execute(
            text("SELECT id, name FROM users WHERE email = :email"),
            {"email": request.email}
        ).fetchone()
        
        if not user:
            # Don't reveal if email exists or not for security
            return {
                "success": True,
                "message": "If this email exists, you will receive a password reset code"
            }
        
        # Send password reset email
        result = email_service.send_password_reset_email(
            email=request.email,
            name=user[1] or "User"
        )
        
        if result["success"]:
            return {
                "success": True,
                "message": "Password reset code sent to your email",
                "email": request.email,
                "otp": result.get("otp")  # For testing - remove in production
            }
        else:
            return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send password reset: {str(e)}")

@router.post("/reset-password")
async def reset_password(request: ResetPasswordRequest, db: Session = Depends(get_db)):
    """Reset password with OTP verification"""
    try:
        # Validate passwords match
        if request.new_password != request.confirm_password:
            return {
                "success": False,
                "message": "Passwords do not match"
            }
        
        # Validate password strength
        if len(request.new_password) < 6:
            return {
                "success": False,
                "message": "Password must be at least 6 characters long"
            }
        
        # Verify OTP first
        otp_result = email_service.get_stored_otp(request.email, purpose="password_reset")
        
        if not otp_result:
            return {
                "success": False,
                "message": "No password reset request found for this email"
            }
        
        if otp_result["otp"] != request.otp:
            return {
                "success": False,
                "message": "Invalid reset code"
            }
        
        from datetime import datetime
        if otp_result["expires_at"] < datetime.utcnow():
            return {
                "success": False,
                "message": "Reset code has expired"
            }
        
        # Check if user exists
        from sqlalchemy import text
        user = db.execute(
            text("SELECT id FROM users WHERE email = :email"),
            {"email": request.email}
        ).fetchone()
        
        if not user:
            return {
                "success": False,
                "message": "User not found"
            }
        
        # Hash new password
        hashed_password = bcrypt.hashpw(request.new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # Update password
        db.execute(
            text("UPDATE users SET password = :password, updated_at = CURRENT_TIMESTAMP WHERE email = :email"),
            {"password": hashed_password, "email": request.email}
        )
        
        # Remove used OTP
        email_service.remove_otp(request.email, purpose="password_reset")
        
        db.commit()
        
        return {
            "success": True,
            "message": "Password reset successfully"
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Password reset failed: {str(e)}")

@router.post("/change-password")
async def change_password(request: ChangePasswordRequest, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    """Change password for authenticated user"""
    try:
        # Validate passwords match
        if request.new_password != request.confirm_password:
            return {
                "success": False,
                "message": "New passwords do not match"
            }
        
        # Validate password strength
        if len(request.new_password) < 6:
            return {
                "success": False,
                "message": "Password must be at least 6 characters long"
            }
        
        # Get current user's password
        from sqlalchemy import text
        user = db.execute(
            text("SELECT password FROM users WHERE id = :user_id"),
            {"user_id": current_user["user_id"]}
        ).fetchone()
        
        if not user:
            return {
                "success": False,
                "message": "User not found"
            }
        
        # Verify current password
        if not bcrypt.checkpw(request.current_password.encode('utf-8'), user[0].encode('utf-8')):
            return {
                "success": False,
                "message": "Current password is incorrect"
            }
        
        # Hash new password
        hashed_password = bcrypt.hashpw(request.new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # Update password
        db.execute(
            text("UPDATE users SET password = :password, updated_at = CURRENT_TIMESTAMP WHERE id = :user_id"),
            {"password": hashed_password, "user_id": current_user["user_id"]}
        )
        
        db.commit()
        
        return {
            "success": True,
            "message": "Password changed successfully"
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Password change failed: {str(e)}")

@router.post("/resend-otp")
async def resend_otp(request: ResendVerificationRequest, db: Session = Depends(get_db)):
    """Resend OTP for email verification or password reset"""
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
        
        # Check if there's an existing OTP request
        existing_otp = email_service.get_stored_otp(request.email, purpose="email_verification")
        password_reset_otp = email_service.get_stored_otp(request.email, purpose="password_reset")
        
        if password_reset_otp:
            # Resend password reset OTP
            result = email_service.send_password_reset_email(
                email=request.email,
                name=user[1] or "User"
            )
            
            if result["success"]:
                return {
                    "success": True,
                    "message": "Password reset code resent",
                    "type": "password_reset",
                    "otp": result.get("otp")  # For testing
                }
            else:
                return result
                
        elif existing_otp or not user[2]:  # Has OTP request or not verified
            # Resend email verification OTP
            result = email_service.send_verification_email(
                email=request.email,
                name=user[1] or "User"
            )
            
            if result["success"]:
                return {
                    "success": True,
                    "message": "Verification code resent",
                    "type": "email_verification",
                    "otp": result.get("otp")  # For testing
                }
            else:
                return result
        else:
            return {
                "success": False,
                "message": "No active OTP request found and email is already verified"
            }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to resend OTP: {str(e)}")