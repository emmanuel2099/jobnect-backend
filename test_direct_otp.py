#!/usr/bin/env python3
"""
Direct test of OTP generation and email simulation
"""

import requests
import os

def test_direct_otp():
    """Test Botoi API directly and simulate email sending"""
    print("🧪 Direct OTP Test...")
    print("📧 Target Email: emmappdesigner@gmail.com")
    print("-" * 50)
    
    # Test Botoi API
    api_key = "botoi_MvZiT6Lei7rmKrqnTNzTJb"
    base_url = "https://api.botoi.com/v1"
    
    try:
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        
        response = requests.post(
            f'{base_url}/otp/generate',
            json={'length': 6, 'purpose': 'email-verification'},
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            otp = data.get('data', {}).get('code')
            
            print("✅ Botoi API Success!")
            print(f"🔢 Generated OTP: {otp}")
            print(f"⏰ Expires In: {data.get('data', {}).get('expires_in')} seconds")
            
            # Simulate email content
            print("\n📧 Simulated Email Content:")
            print("=" * 50)
            print(f"From: Eagle's Pride <emmappdesigner@gmail.com>")
            print(f"To: emmappdesigner@gmail.com")
            print(f"Subject: 🦅 Verify Your Eagle's Pride Account")
            print("=" * 50)
            print("Hello Test User,")
            print("")
            print("Thank you for joining Eagle's Pride! To complete your account setup,")
            print("please verify your email address using the code below:")
            print("")
            print(f"🔢 Your Verification Code: {otp}")
            print("")
            print("This code expires in 5 minutes. Please enter this code in the app")
            print("to verify your email address.")
            print("")
            print("How to verify:")
            print("1. Open the Eagle's Pride app")
            print("2. Enter the 6-digit code above")
            print("3. Start exploring amazing job opportunities!")
            print("")
            print("Best regards,")
            print("The Eagle's Pride Team")
            print("=" * 50)
            
            print(f"\n🎉 OTP {otp} is ready for testing!")
            print("📱 In the app, use this OTP to complete verification")
            
            return otp
        else:
            print(f"❌ Botoi API Error: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None

if __name__ == "__main__":
    otp = test_direct_otp()
    if otp:
        print(f"\n🔗 SUCCESS! Use OTP {otp} for app testing")
    else:
        print("\n💥 Failed to generate OTP")
