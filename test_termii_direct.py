#!/usr/bin/env python3
"""
Direct test of Termii API to verify it's working
"""

import requests
import json

def test_termii_direct():
    """Test Termii API directly"""
    print("🧪 Testing Termii API Directly...")
    
    api_key = "TLcVqiiQrRXmAHigKcYEPaXetlRVwCxKEftjtSARBXEDqYBbgmoBRtcucLKYsO"
    base_url = "https://v3.api.termii.com"
    
    # Test email OTP
    payload = {
        "api_key": api_key,
        "email_address": "test@example.com",
        "code": "123456"
    }
    
    try:
        print(f"📧 Sending test email to: test@example.com")
        print(f"🔑 Using API Key: {api_key[:20]}...")
        
        response = requests.post(
            f"{base_url}/api/email/otp/send",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"📋 Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Termii API is working!")
            print(f"📧 Response: {json.dumps(data, indent=2)}")
        else:
            print(f"❌ Termii API Error: {response.status_code}")
            print(f"📄 Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Request failed: {e}")

if __name__ == "__main__":
    test_termii_direct()