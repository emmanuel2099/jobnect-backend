#!/usr/bin/env python3
"""
Test registration endpoint directly to see what response is returned
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import requests
import json
import time

def test_registration():
    """Test registration endpoint"""
    print("🧪 Testing Registration Endpoint...")
    print("-" * 50)
    
    backend_url = "https://jobnect-backend-production.up.railway.app/api/v10/registration"
    
    # Test data
    test_data = {
        "name": "Test User",
        "email": f"testuser{int(time.time())}@example.com",  # Use unique email
        "phone": f"{int(time.time())}",
        "password": "password123",
        "password_confirmation": "password123",
        "company": "N/A"
    }
    
    try:
        print(f"📡 Sending request to: {backend_url}")
        print(f"📤 Data: {json.dumps(test_data, indent=2)}")
        
        response = requests.post(backend_url, json=test_data, timeout=5)
        
        print(f"📥 Status Code: {response.status_code}")
        print(f"📥 Response Headers: {dict(response.headers)}")
        
        try:
            response_data = response.json()
            print(f"📥 Response Body: {json.dumps(response_data, indent=2)}")
        except:
            print(f"📥 Raw Response: {response.text}")
        
        # Check if response has success field
        if response.status_code == 200:
            try:
                data = response.json()
                if data.get('success') == True:
                    print("✅ Registration successful!")
                    print(f"📧 Email sent: {data.get('data', {}).get('email_sent', 'Unknown')}")
                    print(f"🔢 OTP: {data.get('data', {}).get('otp', 'Not provided')}")
                    print(f"📧 Service: {data.get('data', {}).get('service', 'Unknown')}")
                else:
                    print("❌ Registration failed!")
                    print(f"📄 Message: {data.get('message', 'No message')}")
            except:
                print("❌ Invalid JSON response")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            
    except requests.exceptions.Timeout:
        print("❌ Request timeout - backend might be down or slow")
    except requests.exceptions.ConnectionError:
        print("❌ Connection error - backend might be down")
    except Exception as e:
        print(f"❌ Test error: {str(e)}")

if __name__ == "__main__":
    test_registration()
