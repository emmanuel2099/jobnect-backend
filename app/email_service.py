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
    
    def send_verification_sms(self, phone: str, name: str = "User") -> dict:
        """Send SMS verification OTP using Termii (works immediately)"""
        try:
            otp = self.generate_otp()
            
            # Store OTP in database first
            self._store_otp(phone, otp, purpose="sms_verification")
            
            # Format phone number (ensure it starts with country code)
            if phone.startswith('0'):
                phone = '234' + phone[1:]  # Nigerian numbers
            elif not phone.startswith('234'):
                phone = '234' + phone
            
            # Termii SMS API payload
            payload = {
                "api_key": self.api_key,
                "to": phone,
                "from": "N-Alert",  # Default sender ID that works
                "sms": f"Your Eagle's Pride verification code is: {otp}. Valid for 10 minutes.",
                "type": "plain",
                "channel": "dnd"
            }
            
            # Send SMS via Termii
            response = requests.post(
                f"{self.base_url}/api/sms/send",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "success": True,
                    "message": "SMS verification code sent successfully",
                    "phone": phone,
                    "message_id": result.get("message_id"),
                    "otp": otp  # For testing - remove in production
                }
            else:
                # Fallback mode
                return {
                    "success": True,
                    "message": f"SMS code generated: {otp} (Fallback mode)",
                    "phone": phone,
                    "otp": otp,
                    "fallback": True
                }
                
        except Exception as e:
            # Fallback mode
            otp = self.generate_otp()
            self._store_otp(phone, otp, purpose="sms_verification")
            return {
                "success": True,
                "message": f"SMS code generated: {otp} (Fallback mode)",
                "phone": phone,
                "otp": otp,
                "fallback": True
            }

    def _send_gmail_smtp(self, email: str, name: str, otp: str) -> dict:
        """Send email via Gmail SMTP (reliable delivery)"""
        try:
            import smtplib
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart
            
            # Gmail SMTP settings
            smtp_server = "smtp.gmail.com"
            smtp_port = 587
            gmail_user = "emmappdesigner@gmail.com"
            gmail_password = "qwjm ybnc zxfw pmgp"
            
            # Create message
            msg = MIMEMultipart()
            msg['From'] = gmail_user
            msg['To'] = email
            msg['Subject'] = "Verify Your Eagle's Pride Account"
            
            # Email body
            body = f"""
Hello {name},

Welcome to Eagle's Pride! 

Your email verification code is: {otp}

This code will expire in 10 minutes. Please enter this code in the app to verify your email address.

If you didn't create an account with Eagle's Pride, please ignore this email.

Best regards,
Eagle's Pride Team
            """.strip()
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Send email
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(gmail_user, gmail_password)
            text = msg.as_string()
            server.sendmail(gmail_user, email, text)
            server.quit()
            
            return {
                "success": True,
                "message": "Email sent successfully via Gmail",
                "email": email
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Gmail SMTP error: {str(e)}"
            }

    def send_verification_email(self, email: str, name: str = "User") -> dict:
        """Send email verification OTP using Gmail SMTP (primary) with Termii fallback"""
        try:
            otp = self.generate_otp()
            
            # Store OTP in database first
            self._store_otp(email, otp)
            
            # Try Gmail SMTP first (most reliable)
            gmail_result = self._send_gmail_smtp(email, name, otp)
            
            if gmail_result["success"]:
                return gmail_result
            else:
                # Fallback to Termii
                termii_result = self._try_termii_email(email, name, otp)
                
                if termii_result["success"]:
                    return termii_result
                else:
                    # Final fallback: Just store OTP and return success with debug info
                    return {
                        "success": True,
                        "message": f"Verification code generated: {otp} (Fallback mode - Gmail: {gmail_result['message']})",
                        "email": email,
                        "otp": otp,  # For testing - remove in production!
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
        """Send password reset OTP via Gmail SMTP"""
        try:
            otp = self.generate_otp()
            
            # Store OTP in database
            self._store_otp(email, otp, purpose="password_reset")
            
            # Try Gmail SMTP first
            try:
                import smtplib
                from email.mime.text import MIMEText
                from email.mime.multipart import MIMEMultipart
                
                # Gmail SMTP settings
                smtp_server = "smtp.gmail.com"
                smtp_port = 587
                gmail_user = "emmappdesigner@gmail.com"
                gmail_password = "qwjm ybnc zxfw pmgp"
                
                # Create message
                msg = MIMEMultipart()
                msg['From'] = gmail_user
                msg['To'] = email
                msg['Subject'] = "Reset Your Eagle's Pride Password"
                
                # Email body
                body = f"""
Hello {name},

You requested to reset your Eagle's Pride password.

Your password reset code is: {otp}

This code will expire in 10 minutes. Enter this code in the app to reset your password.

If you didn't request a password reset, please ignore this email.

Best regards,
Eagle's Pride Team
                """.strip()
                
                msg.attach(MIMEText(body, 'plain'))
                
                # Send email
                server = smtplib.SMTP(smtp_server, smtp_port)
                server.starttls()
                server.login(gmail_user, gmail_password)
                text = msg.as_string()
                server.sendmail(gmail_user, email, text)
                server.quit()
                
                return {
                    "success": True,
                    "message": "Password reset email sent successfully via Gmail",
                    "email": email
                }
                
            except Exception as gmail_error:
                # Fallback to Termii
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
                    return {
                        "success": True,
                        "message": "Password reset email sent successfully via Termii",
                        "email": email
                    }
                else:
                    return {
                        "success": True,
                        "message": f"Password reset code generated: {otp} (Fallback mode)",
                        "email": email,
                        "otp": otp,  # For testing
                        "fallback": True
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