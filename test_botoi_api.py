#!/usr/bin/env python3
"""
Test Botoi API for OTP generation
"""

import requests
import json

def test_botoi_api():
    """Test Botoi API OTP generation"""
    api_key = "botoi_MvZiT6Lei7rmKrqnTNzTJb"
    base_url = "https://api.botoi.com/v1"
    
    print("🧪 Testing Botoi API...")
    print(f"API Key: {api_key}")
    print(f"Base URL: {base_url}")
    print("-" * 50)
    
    try:
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'length': 6,
            'purpose': 'email-verification'
        }
        
        print("📤 Sending request...")
        print(f"Headers: {headers}")
        print(f"Payload: {payload}")
        print("-" * 50)
        
        response = requests.post(
            f'{base_url}/otp/generate',
            json=payload,
            headers=headers,
            timeout=30
        )
        
        print(f"📥 Response Status: {response.status_code}")
        print(f"📥 Response Headers: {dict(response.headers)}")
        print(f"📥 Response Body: {response.text}")
        print("-" * 50)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ SUCCESS!")
            print(f"🔢 Generated OTP: {data.get('otp')}")
            print(f"📋 Full Response: {json.dumps(data, indent=2)}")
            return True
        else:
            print("❌ FAILED!")
            print(f"Error: {response.status_code} - {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ TIMEOUT - Request took too long")
        return False
    except requests.exceptions.ConnectionError:
        print("❌ CONNECTION ERROR - Could not connect to Botoi API")
        return False
    except Exception as e:
        print(f"❌ ERROR - {str(e)}")
        return False

if __name__ == "__main__":
    success = test_botoi_api()
    if success:
        print("\n🎉 Botoi API test completed successfully!")
    else:
        print("\n💥 Botoi API test failed!")
    print("\n🔗 Ready to test in app if API is working.")
