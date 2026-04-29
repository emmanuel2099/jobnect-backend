#!/usr/bin/env python3
"""
Test email service directly to see if it's working
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.email_service import EmailService

def test_email_service():
    """Test email service OTP generation and sending"""
    print("🧪 Testing Email Service...")
    print("-" * 50)
    
    try:
        email_service = EmailService()
        
        # Test OTP generation and email sending
        print("📧 Testing OTP generation and email sending...")
        result = email_service.send_verification_email(
            email="test@example.com",
            name="Test User"
        )
        
        print(f"📥 Result: {result}")
        
        if result.get("success"):
            print("✅ Email service working!")
            print(f"📧 Email sent: {result.get('email_sent', False)}")
            print(f"🔢 OTP: {result.get('otp', 'Not provided')}")
            print(f"📧 Service: {result.get('service', 'Unknown')}")
        else:
            print("❌ Email service failed!")
            print(f"📄 Message: {result.get('message', 'No message')}")
            
    except Exception as e:
        print(f"❌ Test error: {str(e)}")
        import traceback
        print(f"❌ Traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    test_email_service()
