#!/usr/bin/env python3
"""
Test Termii SMS OTP API instead of email
"""

import requests
import json

def test_termii_sms():
    """Test Termii SMS OTP API"""
    print("🧪 Testing Termii SMS OTP API...")
    
    api_key = "TLcVqiiQrRXmAHigKcYEPaXetlRVwCxKEftjtSARBXEDqYBbgmoBRtcucLKYsO"
    base_url = "https://v3.api.termii.com"
    
    # Test SMS OTP
    payload = {
        "api_key": api_key,
        "to": "2348123456789",  # Test Nigerian number
        "from": "EaglesPride",
        "sms": "Your Eagle's Pride verification code is: 123456. This code expires in 10 minutes.",
        "channel": "dnd",  # Use DND for OTP messages
        "type": "plain"
    }
    
    try:
        print(f"📱 Sending test SMS to: 2348123456789")
        print(f"🔑 Using API Key: {api_key[:20]}...")
        
        response = requests.post(
            f"{base_url}/api/sms/send",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"📋 Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Termii SMS API is working!")
            print(f"📱 Response: {json.dumps(data, indent=2)}")
        else:
            print(f"❌ Termii SMS API Error: {response.status_code}")
            print(f"📄 Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Request failed: {e}")

if __name__ == "__main__":
    test_termii_sms()