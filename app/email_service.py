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
        # Botoi API Configuration
        self.botoi_api_key = os.getenv("BOTOI_API_KEY")
        self.botoi_base_url = "https://api.botoi.com/v1"
        
        # Gmail SMTP Configuration (Backup - may be blocked on Render)
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.gmail_user = os.getenv("GMAIL_USER")
        self.gmail_password = os.getenv("GMAIL_PASSWORD")
        
        # Resend API Configuration (HTTPS-based, works on Render)
        self.resend_api_key = os.getenv("RESEND_API_KEY")
        self.resend_from = os.getenv("RESEND_FROM_EMAIL", "Eagle's Pride <noreply@eaglespride.com.ng>")
        
    def _generate_botoi_otp(self) -> dict:
        """Generate OTP using Botoi API"""
        try:
            headers = {
                'Authorization': f'Bearer {self.botoi_api_key}',
                'Content-Type': 'application/json'
            }
            
            response = requests.post(
                f'{self.botoi_base_url}/otp/generate',
                json={'length': 6, 'purpose': 'email-verification'},
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "otp": data.get('data', {}).get('code'),
                    "message": "OTP generated successfully via Botoi API"
                }
            else:
                return {
                    "success": False,
                    "message": f"Botoi API error: {response.status_code} - {response.text}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "message": f"Botoi API connection error: {str(e)}"
            }
    
    def generate_otp(self, length: int = 6) -> str:
        """Generate a random OTP code (fallback)"""
        return ''.join(random.choices(string.digits, k=length))
    
    def _send_via_resend(self, email: str, name: str, otp: str, subject: str = None, purpose: str = "verification") -> dict:
        """Send email via Resend API (HTTPS-based, works on Render free tier)"""
        try:
            if not self.resend_api_key:
                return {"success": False, "message": "Resend API key not configured"}
            
            if subject is None:
                subject = "🦅 Verify Your Eagle's Pride Account" if purpose == "verification" else "🔐 Reset Your Eagle's Pride Password"
            
            html_body = self._build_email_html(name, otp, purpose)
            text_body = self._build_email_text(name, otp, purpose)
            
            from_address = self.resend_from
            
            response = requests.post(
                "https://api.resend.com/emails",
                headers={
                    "Authorization": f"Bearer {self.resend_api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "from": from_address,
                    "to": [email],
                    "subject": subject,
                    "html": html_body,
                    "text": text_body
                },
                timeout=15
            )
            
            if response.status_code in (200, 201):
                return {"success": True, "message": "Email sent via Resend", "email": email}
            else:
                error_detail = ""
                try:
                    resp_json = response.json()
                    error_detail = resp_json.get("message", response.text)
                    # Domain not verified — this is expected until eaglespride.com.ng is added to Resend
                    if "verify a domain" in error_detail or "testing emails" in error_detail:
                        return {
                            "success": False,
                            "message": "domain_not_verified",
                            "detail": error_detail
                        }
                except Exception:
                    error_detail = response.text
                return {"success": False, "message": f"Resend error {response.status_code}: {error_detail}"}
        except Exception as e:
            return {"success": False, "message": f"Resend API error: {str(e)}"}

    def _build_email_html(self, name: str, otp: str, purpose: str = "verification") -> str:
        """Build branded HTML email body"""
        title = "Welcome to Eagle's Pride!" if purpose == "verification" else "Password Reset"
        intro = (
            "Thank you for joining Eagle's Pride! To complete your account setup, please verify your email address using the code below:"
            if purpose == "verification"
            else "You requested to reset your Eagle's Pride password. Use the verification code below to proceed:"
        )
        code_label = "Your Verification Code" if purpose == "verification" else "Password Reset Code"
        
        return f"""<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"></head>
<body style="margin:0;padding:0;font-family:'Segoe UI',Tahoma,Geneva,Verdana,sans-serif;background-color:#f5f5f5;">
  <div style="max-width:600px;margin:0 auto;background:#fff;border-radius:10px;overflow:hidden;box-shadow:0 4px 6px rgba(0,0,0,0.1);">
    <div style="background:linear-gradient(135deg,#D84315 0%,#FF5722 100%);padding:30px 20px;text-align:center;">
      <h1 style="color:white;margin:0;font-size:28px;font-weight:bold;">🦅 Eagle's Pride</h1>
      <p style="color:rgba(255,255,255,0.9);margin:8px 0 0;font-size:16px;">Your Gateway to Career Success</p>
    </div>
    <div style="padding:40px 30px;">
      <h2 style="color:#333;text-align:center;">{title}</h2>
      <p style="color:#666;font-size:16px;line-height:1.6;">Hello <strong>{name}</strong>,</p>
      <p style="color:#666;font-size:16px;line-height:1.6;">{intro}</p>
      <div style="background:linear-gradient(135deg,#D84315 0%,#FF5722 100%);border-radius:12px;padding:25px;text-align:center;margin:30px 0;">
        <p style="color:white;margin:0 0 10px;font-size:14px;text-transform:uppercase;letter-spacing:1px;">{code_label}</p>
        <div style="background:rgba(255,255,255,0.15);border-radius:8px;padding:15px;display:inline-block;">
          <span style="color:white;font-size:36px;font-weight:bold;letter-spacing:10px;font-family:'Courier New',monospace;">{otp}</span>
        </div>
        <p style="color:rgba(255,255,255,0.9);margin:10px 0 0;font-size:12px;">This code expires in 10 minutes</p>
      </div>
      <div style="border-left:4px solid #D84315;padding:15px;background:#fff3e0;border-radius:4px;">
        <p style="color:#666;font-size:14px;margin:0;">🔒 If you didn't request this, please ignore this email.</p>
      </div>
    </div>
    <div style="background:#f8f9fa;padding:25px 30px;text-align:center;border-top:1px solid #eee;">
      <p style="color:#999;font-size:14px;margin:0;">Best regards,<br><strong style="color:#D84315;">The Eagle's Pride Team</strong></p>
      <p style="color:#ccc;font-size:12px;margin:8px 0 0;">© 2026 Eagle's Pride. Empowering careers, connecting opportunities.</p>
    </div>
  </div>
</body>
</html>"""

    def _build_email_text(self, name: str, otp: str, purpose: str = "verification") -> str:
        """Build plain text email body"""
        action = "verify your email" if purpose == "verification" else "reset your password"
        return f"""Hello {name},

Your Eagle's Pride code to {action} is: {otp}

This code expires in 10 minutes.

If you didn't request this, please ignore this email.

Best regards,
The Eagle's Pride Team"""
    
    def _send_gmail_smtp_reset(self, email: str, name: str, otp: str) -> dict:
        """Send password reset email via Gmail SMTP"""
        return self._send_gmail_smtp(email, name, otp)

    def _send_gmail_smtp(self, email: str, name: str, otp: str) -> dict:
        """Send email via Gmail SMTP (reliable delivery) with branded HTML template"""
        try:
            import smtplib
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart
            
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = f"Eagle's Pride <{self.gmail_user}>"
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
            
            # Send email with timeout
            server = smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=10)
            server.starttls(timeout=5)
            server.login(self.gmail_user, self.gmail_password)
            text = msg.as_string()
            server.sendmail(self.gmail_user, email, text)
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
        """Send email verification OTP - tries Resend API first, then Gmail SMTP"""
        try:
            otp = self.generate_otp()
            self._store_otp(email, otp, purpose="email_verification")
            
            # Try Resend API first (works on Render - HTTPS based)
            if self.resend_api_key:
                result = self._send_via_resend(email, name, otp, purpose="verification")
                if result["success"]:
                    return {
                        "success": True,
                        "message": "Verification email sent",
                        "email": email,
                        "email_sent": True,
                        "service": "resend"
                    }
            
            # Fallback: try Gmail SMTP
            gmail_result = self._send_gmail_smtp(email, name, otp)
            if gmail_result.get("success"):
                return {
                    "success": True,
                    "message": "Verification email sent",
                    "email": email,
                    "email_sent": True,
                    "service": "gmail"
                }
            
            # Both failed — OTP is stored, return it so app can show it
            print(f"[EMAIL FALLBACK] OTP for {email}: {otp} (email delivery failed)")
            return {
                "success": True,
                "message": "OTP generated. Email delivery failed — check spam or contact support.",
                "email": email,
                "email_sent": False,
                "otp": otp  # Remove this in production once email is working
            }
                
        except Exception as e:
            return {
                "success": False,
                "message": f"Email service error: {str(e)}"
            }
    
    def verify_email_otp(self, email: str, otp: str) -> dict:
        """Verify the email OTP code"""
        try:
            # Check OTP from database
            stored_otp = self.get_stored_otp(email)
            
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
            self.remove_otp(email)
            
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
        """Send password reset OTP - tries Resend API first, then Gmail SMTP"""
        try:
            otp = self.generate_otp()
            self._store_otp(email, otp, purpose="password_reset")
            
            # Try Resend API first
            if self.resend_api_key:
                result = self._send_via_resend(
                    email, name, otp,
                    subject="🔐 Reset Your Eagle's Pride Password",
                    purpose="reset"
                )
                if result["success"]:
                    return {
                        "success": True,
                        "message": "Password reset email sent",
                        "email": email,
                        "email_sent": True
                    }
            
            # Fallback: Gmail SMTP
            try:
                gmail_result = self._send_gmail_smtp_reset(email, name, otp)
                if gmail_result.get("success"):
                    return {
                        "success": True,
                        "message": "Password reset email sent",
                        "email": email,
                        "email_sent": True
                    }
            except Exception:
                pass
            
            # Both failed
            print(f"[EMAIL FALLBACK] Password reset OTP for {email}: {otp}")
            return {
                "success": True,
                "message": "Reset code generated. Email delivery failed — check spam or contact support.",
                "email": email,
                "email_sent": False,
                "otp": otp  # Remove once email is working
            }
                
        except Exception as e:
            return {
                "success": False,
                "message": f"Password reset error: {str(e)}"
            }
    
    def _store_otp(self, email: str, otp: str, purpose: str = "email_verification"):
        """Store OTP in database with expiration - creates table if needed"""
        try:
            # Try to use production database first, fallback to local
            from .database import get_db, SessionLocal
            from sqlalchemy import text
            
            try:
                # Try production database
                db = next(get_db())
            except:
                # Fallback to local database
                db = SessionLocal()
            
            try:
                # Try to create table if it doesn't exist
                try:
                    db.execute(text("""
                        CREATE TABLE IF NOT EXISTS email_otps (
                            id SERIAL PRIMARY KEY,
                            email VARCHAR(255) NOT NULL,
                            otp VARCHAR(10) NOT NULL,
                            purpose VARCHAR(50) DEFAULT 'email_verification',
                            expires_at TIMESTAMP NOT NULL,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                    """))
                    db.commit()
                except:
                    # Table might already exist, continue
                    pass
                
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
            # Don't fail completely - we can still return the OTP for testing
    
    def get_stored_otp(self, email: str, purpose: str = "email_verification") -> Optional[dict]:
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
                else:
                    return None
            finally:
                db.close()
        
        except Exception as e:
            print(f"Error getting OTP: {e}")
            return None
    
    def remove_otp(self, email: str, purpose: str = "email_verification"):
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