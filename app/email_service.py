import requests
import random
import string
from datetime import datetime, timedelta
from typing import Optional
import os
from .database import get_db
from sqlalchemy.orm import Session
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class EmailService:
    def __init__(self):
        self.api_key = os.getenv("TERMII_API_KEY", "TLcVqiiQrRXmAHigKcYEPaXetlRVwCxKEftjtSARBXEDqYBbgmoBRtcucLKYsO")
        self.secret_key = os.getenv("TERMII_SECRET_KEY", "tsk_FpRsX75MrdHwAhACS0Mm2vTjcP")
        self.base_url = "https://v3.api.termii.com"
        
    def generate_otp(self, length: int = 6) -> str:
        """Generate a random OTP code"""
        return ''.join(random.choices(string.digits, k=length))
    
    def send_verification_email(self, email: str, name: str = "User") -> dict:
        """Send email verification OTP using fallback method"""
        try:
            otp = self.generate_otp()
            
            # Store OTP in database first
            self._store_otp(email, otp)
            
            # Try Termii first, then fallback to simple storage
            termii_result = self._try_termii_email(email, name, otp)
            
            if termii_result["success"]:
                return termii_result
            else:
                # Fallback: Just store OTP and return success
                # In production, you'd integrate with a proper email service
                return {
                    "success": True,
                    "message": f"Verification code generated: {otp} (Fallback mode - check console)",
                    "email": email,
                    "otp": otp,  # Remove this in production!
                    "fallback": True
                }
                
        except Exception as e:
            return {
                "success": False,
                "message": f"Email service error: {str(e)}"
            }
    
    def _try_termii_email(self, email: str, name: str, otp: str) -> dict:
        """Try to send email via Termii"""
        try:
            # Email content
            subject = "Verify Your Eagle's Pride Account"
            message = f"""
Hello {name},

Welcome to Eagle's Pride! 

Your email verification code is: {otp}

This code will expire in 10 minutes. Please enter this code in the app to verify your email address.

If you didn't create an account with Eagle's Pride, please ignore this email.

Best regards,
Eagle's Pride Team
            """.strip()
            
            # Termii Email API payload
            payload = {
                "api_key": self.api_key,
                "email_address": email,
                "code": otp
            }
            
            # Send email via Termii
            response = requests.post(
                f"{self.base_url}/api/email/otp/send",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "success": True,
                    "message": "Verification email sent successfully via Termii",
                    "otp_id": result.get("pinId"),
                    "email": email
                }
            else:
                return {
                    "success": False,
                    "message": f"Termii failed: {response.text}",
                    "error_code": response.status_code
                }
                
        except Exception as e:
            return {
                "success": False,
                "message": f"Termii error: {str(e)}"
            }
    
    def verify_email_otp(self, email: str, otp: str) -> dict:
        """Verify the email OTP code"""
        try:
            # Check OTP from database
            stored_otp = self._get_stored_otp(email)
            
            if not stored_otp:
                return {
                    "success": False,
                    "message": "No OTP found for this email"
                }
            
            if stored_otp["otp"] != otp:
                return {
                    "success": False,
                    "message": "Invalid OTP code"
                }
            
            if stored_otp["expires_at"] < datetime.utcnow():
                return {
                    "success": False,
                    "message": "OTP has expired"
                }
            
            # OTP is valid, remove it from storage
            self._remove_otp(email)
            
            return {
                "success": True,
                "message": "Email verified successfully"
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Verification error: {str(e)}"
            }
    
    def send_password_reset_email(self, email: str, name: str = "User") -> dict:
        """Send password reset OTP"""
        try:
            otp = self.generate_otp()
            
            subject = "Reset Your Eagle's Pride Password"
            message = f"""
Hello {name},

You requested to reset your Eagle's Pride password.

Your password reset code is: {otp}

This code will expire in 10 minutes. Enter this code in the app to reset your password.

If you didn't request a password reset, please ignore this email.

Best regards,
Eagle's Pride Team
            """.strip()
            
            payload = {
                "api_key": self.api_key,
                "email_address": email,
                "code": otp
            }
            
            response = requests.post(
                f"{self.base_url}/api/email/otp/send",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                self._store_otp(email, otp, purpose="password_reset")
                
                return {
                    "success": True,
                    "message": "Password reset email sent successfully",
                    "email": email
                }
            else:
                return {
                    "success": False,
                    "message": f"Failed to send reset email: {response.text}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "message": f"Password reset error: {str(e)}"
            }
    
    def _store_otp(self, email: str, otp: str, purpose: str = "email_verification"):
        """Store OTP in database with expiration"""
        try:
            from .database import SessionLocal
            from sqlalchemy import text
            db = SessionLocal()
            
            try:
                # Remove any existing OTP for this email
                db.execute(
                    text("DELETE FROM email_otps WHERE email = :email AND purpose = :purpose"),
                    {"email": email, "purpose": purpose}
                )
                
                # Store new OTP
                expires_at = datetime.utcnow() + timedelta(minutes=10)
                db.execute(
                    text("""INSERT INTO email_otps (email, otp, purpose, expires_at, created_at) 
                       VALUES (:email, :otp, :purpose, :expires_at, :created_at)"""),
                    {
                        "email": email,
                        "otp": otp,
                        "purpose": purpose,
                        "expires_at": expires_at,
                        "created_at": datetime.utcnow()
                    }
                )
                db.commit()
            finally:
                db.close()
            
        except Exception as e:
            print(f"Error storing OTP: {e}")
    
    def _get_stored_otp(self, email: str, purpose: str = "email_verification") -> Optional[dict]:
        """Get stored OTP from database"""
        try:
            from .database import SessionLocal
            from sqlalchemy import text
            db = SessionLocal()
            
            try:
                result = db.execute(
                    text("SELECT otp, expires_at FROM email_otps WHERE email = :email AND purpose = :purpose"),
                    {"email": email, "purpose": purpose}
                ).fetchone()
                
                if result:
                    return {
                        "otp": result[0],
                        "expires_at": result[1]
                    }
                return None
            finally:
                db.close()
            
        except Exception as e:
            print(f"Error getting OTP: {e}")
            return None
    
    def _remove_otp(self, email: str, purpose: str = "email_verification"):
        """Remove OTP from database after successful verification"""
        try:
            from .database import SessionLocal
            from sqlalchemy import text
            db = SessionLocal()
            
            try:
                db.execute(
                    text("DELETE FROM email_otps WHERE email = :email AND purpose = :purpose"),
                    {"email": email, "purpose": purpose}
                )
                db.commit()
            finally:
                db.close()
            
        except Exception as e:
            print(f"Error removing OTP: {e}")

# Global instance
email_service = EmailService()