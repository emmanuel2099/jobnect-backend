#!/usr/bin/env python3
"""
Test complete OTP email flow - Botoi API + Gmail SMTP
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.email_service import EmailService

def test_complete_otp_flow():
    """Test complete OTP generation and email sending"""
    print("🧪 Testing Complete OTP Flow...")
    print("📧 Email: emmappdesigner@gmail.com")
    print("👤 Name: Test User")
    print("-" * 60)
    
    # Initialize email service
    email_service = EmailService()
    
    print("🔧 Configuration Check:")
    botoi_key = email_service.botoi_api_key
    print(f"   Botoi API Key: {botoi_key[:20] + '...' if botoi_key else 'Not configured'}")
    print(f"   Gmail User: {email_service.gmail_user}")
    print(f"   Gmail Password: {'*' * len(email_service.gmail_password) if email_service.gmail_password else 'Not configured'}")
    print("-" * 60)
    
    # Test email verification
    print("📤 Sending verification email...")
    result = email_service.send_verification_email(
        email="emmappdesigner@gmail.com",
        name="Test User"
    )
    
    print(f"📥 Result: {result}")
    print("-" * 60)
    
    if result.get("success"):
        print("✅ SUCCESS!")
        print(f"🔢 Generated OTP: {result.get('otp')}")
        print(f"📧 Email Sent: {'Yes' if result.get('email_sent') else 'No'}")
        print(f"🔧 Service Used: {result.get('service')}")
        print(f"📝 Message: {result.get('message')}")
        
        if result.get('email_sent'):
            print("\n🎉 Email should arrive in emmappdesigner@gmail.com shortly!")
            print("📱 Check your inbox for the OTP verification email")
        else:
            print("\n⚠️  OTP generated but email failed - check OTP manually:")
            print(f"   🔢 Manual OTP: {result.get('otp')}")
    else:
        print("❌ FAILED!")
        print(f"📝 Error: {result.get('message')}")
    
    print("\n" + "=" * 60)
    print("🔗 Test completed!")

if __name__ == "__main__":
    test_complete_otp_flow()
