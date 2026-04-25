#!/usr/bin/env python3
"""
Test Termii Token API for OTP verification
"""

import requests
import json

def test_termii_token_api():
    """Test Termii Token API for sending OTP"""
    print("🧪 Testing Termii Token API...")
    
    api_key = "TLcVqiiQrRXmAHigKcYEPaXetlRVwCxKEftjtSARBXEDqYBbgmoBRtcucLKYsO"
    secret_key = "tsk_FpRsX75MrdHwAhACS0Mm2vTjcP"
    base_url = "https://v3.api.termii.com"
    
    # Test Token Send API
    payload = {
        "api_key": api_key,
        "message_type": "NUMERIC",
        "to": "2348123456789",  # Test Nigerian number
        "from": "N-Alert",  # Generic sender ID
        "channel": "dnd",
        "pin_attempts": 10,
        "pin_time_to_live": 5,
        "pin_length": 6,
        "pin_placeholder": "< 1234 >",
        "message_text": "Your Eagle's Pride verification code is < 1234 >. Valid for 5 minutes.",
        "pin_type": "NUMERIC"
    }
    
    try:
        print(f"📱 Sending OTP token to: 2348123456789")
        print(f"🔑 Using API Key: {api_key[:20]}...")
        
        response = requests.post(
            f"{base_url}/api/sms/otp/send",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"📋 Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Termii Token API is working!")
            print(f"📱 Response: {json.dumps(data, indent=2)}")
            
            # Extract pin_id for verification test
            pin_id = data.get("pinId")
            if pin_id:
                print(f"\n🔐 Pin ID for verification: {pin_id}")
                print("📝 You can now test verification with this pin_id")
                
        else:
            print(f"❌ Termii Token API Error: {response.status_code}")
            print(f"📄 Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Request failed: {e}")

def test_termii_verify_token():
    """Test verifying a token (you need to provide pin_id and pin)"""
    print("\n🔍 Testing Token Verification...")
    
    api_key = "TLcVqiiQrRXmAHigKcYEPaXetlRVwCxKEftjtSARBXEDqYBbgmoBRtcucLKYsO"
    base_url = "https://v3.api.termii.com"
    
    # You would get these from the send response and user input
    pin_id = input("Enter pin_id from send response (or press Enter to skip): ").strip()
    pin = input("Enter the 6-digit PIN you received (or press Enter to skip): ").strip()
    
    if not pin_id or not pin:
        print("⏭️ Skipping verification test")
        return
    
    payload = {
        "api_key": api_key,
        "pin_id": pin_id,
        "pin": pin
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/sms/otp/verify",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"📊 Verification Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Token verification response:")
            print(f"📱 Response: {json.dumps(data, indent=2)}")
        else:
            print(f"❌ Verification Error: {response.status_code}")
            print(f"📄 Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Verification failed: {e}")

if __name__ == "__main__":
    test_termii_token_api()
    test_termii_verify_token()