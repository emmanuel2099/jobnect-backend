#!/usr/bin/env python3
"""
Simple test of Termii API with different sender IDs
"""

import requests
import json

def test_termii_with_different_senders():
    """Test Termii with different sender ID options"""
    print("🧪 Testing Termii with different sender IDs...")
    
    api_key = "TLcVqiiQrRXmAHigKcYEPaXetlRVwCxKEftjtSARBXEDqYBbgmoBRtcucLKYsO"
    base_url = "https://v3.api.termii.com"
    
    # Try different sender IDs
    sender_ids = [
        "Termii",      # Default Termii sender
        "TERMII",      # Uppercase
        "2347080",     # Numeric sender
        "Eagles",      # Short brand name
        "EaglesPride", # Full brand name
    ]
    
    for sender_id in sender_ids:
        print(f"\n📱 Testing with sender ID: {sender_id}")
        
        payload = {
            "api_key": api_key,
            "to": "2348123456789",  # Test number
            "from": sender_id,
            "sms": f"Test message from {sender_id}. Your verification code is: 123456",
            "channel": "generic",  # Try generic first
            "type": "plain"
        }
        
        try:
            response = requests.post(
                f"{base_url}/api/sms/send",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            print(f"   📊 Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ SUCCESS with {sender_id}!")
                print(f"   📱 Response: {json.dumps(data, indent=2)}")
                return sender_id  # Return the working sender ID
            else:
                print(f"   ❌ Failed: {response.text[:100]}...")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print("\n❌ No working sender ID found")
    return None

def test_account_balance():
    """Check Termii account balance"""
    print("\n💰 Checking Termii account balance...")
    
    api_key = "TLcVqiiQrRXmAHigKcYEPaXetlRVwCxKEftjtSARBXEDqYBbgmoBRtcucLKYsO"
    base_url = "https://v3.api.termii.com"
    
    try:
        response = requests.get(
            f"{base_url}/api/get-balance?api_key={api_key}",
            timeout=30
        )
        
        print(f"📊 Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Balance check successful!")
            print(f"💰 Response: {json.dumps(data, indent=2)}")
        else:
            print(f"❌ Balance check failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Balance check error: {e}")

if __name__ == "__main__":
    test_account_balance()
    working_sender = test_termii_with_different_senders()
    
    if working_sender:
        print(f"\n🎉 Use this sender ID in your app: {working_sender}")
    else:
        print("\n💡 Recommendation: Contact Termii support to register a sender ID")
        print("   Or use the fallback OTP system we'll implement")