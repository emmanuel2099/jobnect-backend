#!/usr/bin/env python3
"""
Test complete OTP flow - generation, storage, and verification
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.email_service import EmailService

def test_otp_flow():
    """Test complete OTP flow"""
    print("🧪 Testing Complete OTP Flow...")
    print("📧 Test Email: test@example.com")
    print("-" * 60)
    
    # Initialize email service
    email_service = EmailService()
    
    try:
        # Step 1: Generate and store OTP
        print("📤 Step 1: Generating and storing OTP...")
        result = email_service.send_verification_email(
            email="test@example.com",
            name="Test User"
        )
        
        print(f"📥 Result: {result}")
        
        if result.get("success"):
            otp = result.get("otp")
            print(f"✅ OTP Generated: {otp}")
            
            # Step 2: Try to retrieve stored OTP
            print("\n🔍 Step 2: Retrieving stored OTP...")
            stored_otp = email_service.get_stored_otp("test@example.com")
            print(f"📥 Stored OTP: {stored_otp}")
            
            if stored_otp:
                print(f"✅ OTP Found: {stored_otp['otp']}")
                
                # Step 3: Test correct OTP verification
                print("\n✅ Step 3: Testing correct OTP verification...")
                verify_result = email_service.verify_email_otp(
                    email="test@example.com",
                    otp=stored_otp['otp']
                )
                print(f"📥 Verification Result: {verify_result}")
                
                # Step 4: Test wrong OTP verification
                print("\n❌ Step 4: Testing wrong OTP verification...")
                wrong_result = email_service.verify_email_otp(
                    email="test@example.com",
                    otp="000000"
                )
                print(f"📥 Wrong OTP Result: {wrong_result}")
                
            else:
                print("❌ No OTP found in database!")
        else:
            print(f"❌ OTP Generation Failed: {result.get('message')}")
            
    except Exception as e:
        print(f"❌ Test Error: {str(e)}")
        import traceback
        print(f"❌ Traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    test_otp_flow()
