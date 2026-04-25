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
        """Send email via Gmail SMTP (reliable delivery) with branded HTML template"""
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
            msg = MIMEMultipart('alternative')
            msg['From'] = f"Eagle's Pride <{gmail_user}>"
            msg['To'] = email
            msg['Subject'] = "🦅 Verify Your Eagle's Pride Account"
            
            # HTML email template with Eagle's Pride branding
            html_body = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Verify Your Eagle's Pride Account</title>
</head>
<body style="margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f5f5f5;">
    <div style="max-width: 600px; margin: 0 auto; background-color: #ffffff; border-radius: 10px; overflow: hidden; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
        
        <!-- Header with Eagle's Pride Logo -->
        <div style="background: linear-gradient(135deg, #D84315 0%, #FF5722 100%); padding: 30px 20px; text-align: center;">
            <div style="display: inline-flex; align-items: center; justify-content: center; margin-bottom: 10px;">
                <!-- Eagle Logo (using emoji as placeholder - you can replace with actual logo URL) -->
                <div style="width: 60px; height: 60px; background-color: rgba(255,255,255,0.2); border-radius: 50%; display: flex; align-items: center; justify-content: center; margin-right: 15px;">
                    <span style="font-size: 30px;">🦅</span>
                </div>
                <h1 style="color: white; margin: 0; font-size: 28px; font-weight: bold;">Eagle's Pride</h1>
            </div>
            <p style="color: rgba(255,255,255,0.9); margin: 0; font-size: 16px;">Your Gateway to Career Success</p>
        </div>
        
        <!-- Main Content -->
        <div style="padding: 40px 30px;">
            <h2 style="color: #333; margin: 0 0 20px 0; font-size: 24px; text-align: center;">Welcome to Eagle's Pride!</h2>
            
            <p style="color: #666; font-size: 16px; line-height: 1.6; margin-bottom: 30px;">
                Hello <strong>{name}</strong>,
            </p>
            
            <p style="color: #666; font-size: 16px; line-height: 1.6; margin-bottom: 30px;">
                Thank you for joining Eagle's Pride! To complete your account setup, please verify your email address using the code below:
            </p>
            
            <!-- OTP Code Box -->
            <div style="background: linear-gradient(135deg, #D84315 0%, #FF5722 100%); border-radius: 12px; padding: 25px; text-align: center; margin: 30px 0;">
                <p style="color: white; margin: 0 0 10px 0; font-size: 14px; text-transform: uppercase; letter-spacing: 1px;">Your Verification Code</p>
                <div style="background-color: rgba(255,255,255,0.15); border-radius: 8px; padding: 15px; display: inline-block;">
                    <span style="color: white; font-size: 32px; font-weight: bold; letter-spacing: 8px; font-family: 'Courier New', monospace;">{otp}</span>
                </div>
                <p style="color: rgba(255,255,255,0.9); margin: 10px 0 0 0; font-size: 12px;">This code expires in 10 minutes</p>
            </div>
            
            <!-- Instructions -->
            <div style="background-color: #f8f9fa; border-radius: 8px; padding: 20px; margin: 25px 0;">
                <h3 style="color: #D84315; margin: 0 0 15px 0; font-size: 18px;">📱 How to verify:</h3>
                <ol style="color: #666; margin: 0; padding-left: 20px; line-height: 1.6;">
                    <li>Open the Eagle's Pride app</li>
                    <li>Enter the 6-digit code above</li>
                    <li>Start exploring amazing job opportunities!</li>
                </ol>
            </div>
            
            <!-- Security Notice -->
            <div style="border-left: 4px solid #D84315; padding-left: 15px; margin: 25px 0;">
                <p style="color: #666; font-size: 14px; margin: 0; line-height: 1.5;">
                    <strong>🔒 Security Notice:</strong> If you didn't create an account with Eagle's Pride, please ignore this email. Your account security is important to us.
                </p>
            </div>
        </div>
        
        <!-- Footer -->
        <div style="background-color: #f8f9fa; padding: 25px 30px; text-align: center; border-top: 1px solid #eee;">
            <p style="color: #999; font-size: 14px; margin: 0 0 10px 0;">
                Best regards,<br>
                <strong style="color: #D84315;">The Eagle's Pride Team</strong>
            </p>
            <p style="color: #ccc; font-size: 12px; margin: 0;">
                © 2026 Eagle's Pride. Empowering careers, connecting opportunities.
            </p>
        </div>
    </div>
    
    <!-- Mobile Responsive -->
    <style>
        @media only screen and (max-width: 600px) {{
            .container {{ width: 100% !important; }}
            .content {{ padding: 20px !important; }}
        }}
    </style>
</body>
</html>
            """
            
            # Plain text fallback
            text_body = f"""
Hello {name},

Welcome to Eagle's Pride!

Your email verification code is: {otp}

This code will expire in 10 minutes. Please enter this code in the app to verify your email address.

How to verify:
1. Open the Eagle's Pride app
2. Enter the 6-digit code above
3. Start exploring amazing job opportunities!

If you didn't create an account with Eagle's Pride, please ignore this email.

Best regards,
The Eagle's Pride Team

© 2026 Eagle's Pride. Empowering careers, connecting opportunities.
            """.strip()
            
            # Attach both HTML and plain text versions
            msg.attach(MIMEText(text_body, 'plain'))
            msg.attach(MIMEText(html_body, 'html'))
            
            # Send email
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(gmail_user, gmail_password)
            text = msg.as_string()
            server.sendmail(gmail_user, email, text)
            server.quit()
            
            return {
                "success": True,
                "message": "Branded email sent successfully via Gmail",
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
        """Send password reset OTP via Gmail SMTP with branded template"""
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
                msg = MIMEMultipart('alternative')
                msg['From'] = f"Eagle's Pride <{gmail_user}>"
                msg['To'] = email
                msg['Subject'] = "🔐 Reset Your Eagle's Pride Password"
                
                # HTML email template for password reset
                html_body = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Reset Your Eagle's Pride Password</title>
</head>
<body style="margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f5f5f5;">
    <div style="max-width: 600px; margin: 0 auto; background-color: #ffffff; border-radius: 10px; overflow: hidden; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
        
        <!-- Header with Eagle's Pride Logo -->
        <div style="background: linear-gradient(135deg, #D84315 0%, #FF5722 100%); padding: 30px 20px; text-align: center;">
            <div style="display: inline-flex; align-items: center; justify-content: center; margin-bottom: 10px;">
                <div style="width: 60px; height: 60px; background-color: rgba(255,255,255,0.2); border-radius: 50%; display: flex; align-items: center; justify-content: center; margin-right: 15px;">
                    <span style="font-size: 30px;">🦅</span>
                </div>
                <h1 style="color: white; margin: 0; font-size: 28px; font-weight: bold;">Eagle's Pride</h1>
            </div>
            <p style="color: rgba(255,255,255,0.9); margin: 0; font-size: 16px;">Password Reset Request</p>
        </div>
        
        <!-- Main Content -->
        <div style="padding: 40px 30px;">
            <h2 style="color: #333; margin: 0 0 20px 0; font-size: 24px; text-align: center;">🔐 Password Reset</h2>
            
            <p style="color: #666; font-size: 16px; line-height: 1.6; margin-bottom: 30px;">
                Hello <strong>{name}</strong>,
            </p>
            
            <p style="color: #666; font-size: 16px; line-height: 1.6; margin-bottom: 30px;">
                You requested to reset your Eagle's Pride password. Use the verification code below to proceed with resetting your password:
            </p>
            
            <!-- OTP Code Box -->
            <div style="background: linear-gradient(135deg, #D84315 0%, #FF5722 100%); border-radius: 12px; padding: 25px; text-align: center; margin: 30px 0;">
                <p style="color: white; margin: 0 0 10px 0; font-size: 14px; text-transform: uppercase; letter-spacing: 1px;">Password Reset Code</p>
                <div style="background-color: rgba(255,255,255,0.15); border-radius: 8px; padding: 15px; display: inline-block;">
                    <span style="color: white; font-size: 32px; font-weight: bold; letter-spacing: 8px; font-family: 'Courier New', monospace;">{otp}</span>
                </div>
                <p style="color: rgba(255,255,255,0.9); margin: 10px 0 0 0; font-size: 12px;">This code expires in 10 minutes</p>
            </div>
            
            <!-- Instructions -->
            <div style="background-color: #f8f9fa; border-radius: 8px; padding: 20px; margin: 25px 0;">
                <h3 style="color: #D84315; margin: 0 0 15px 0; font-size: 18px;">🔄 How to reset your password:</h3>
                <ol style="color: #666; margin: 0; padding-left: 20px; line-height: 1.6;">
                    <li>Open the Eagle's Pride app</li>
                    <li>Enter the 6-digit code above</li>
                    <li>Create your new secure password</li>
                </ol>
            </div>
            
            <!-- Security Notice -->
            <div style="border-left: 4px solid #ff9800; padding-left: 15px; margin: 25px 0; background-color: #fff3e0; padding: 15px; border-radius: 4px;">
                <p style="color: #e65100; font-size: 14px; margin: 0; line-height: 1.5;">
                    <strong>⚠️ Security Alert:</strong> If you didn't request a password reset, please ignore this email and your password will remain unchanged. Consider updating your account security if you suspect unauthorized access.
                </p>
            </div>
        </div>
        
        <!-- Footer -->
        <div style="background-color: #f8f9fa; padding: 25px 30px; text-align: center; border-top: 1px solid #eee;">
            <p style="color: #999; font-size: 14px; margin: 0 0 10px 0;">
                Best regards,<br>
                <strong style="color: #D84315;">The Eagle's Pride Team</strong>
            </p>
            <p style="color: #ccc; font-size: 12px; margin: 0;">
                © 2026 Eagle's Pride. Empowering careers, connecting opportunities.
            </p>
        </div>
    </div>
</body>
</html>
                """
                
                # Plain text fallback
                text_body = f"""
Hello {name},

You requested to reset your Eagle's Pride password.

Your password reset code is: {otp}

This code will expire in 10 minutes. Enter this code in the app to reset your password.

How to reset your password:
1. Open the Eagle's Pride app
2. Enter the 6-digit code above
3. Create your new secure password

If you didn't request a password reset, please ignore this email.

Best regards,
The Eagle's Pride Team

© 2026 Eagle's Pride. Empowering careers, connecting opportunities.
                """.strip()
                
                # Attach both HTML and plain text versions
                msg.attach(MIMEText(text_body, 'plain'))
                msg.attach(MIMEText(html_body, 'html'))
                
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