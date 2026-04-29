#!/usr/bin/env python3
"""
Test email service on production backend
"""

import requests
import json

def test_production_email():
    """Test email service endpoint directly"""
    print("🧪 Testing Production Email Service...")
    print("-" * 50)
    
    backend_url = "https://jobnect-backend-production.up.railway.app/api/v10/email/send-verification"
    
    # Test data
    test_data = {
        "email": "test@example.com",
        "name": "Test User"
    }
    
    try:
        print(f"📡 Sending request to: {backend_url}")
        print(f"📤 Data: {json.dumps(test_data, indent=2)}")
        
        response = requests.post(backend_url, json=test_data, timeout=5)
        
        print(f"📥 Status Code: {response.status_code}")
        
        try:
            response_data = response.json()
            print(f"📥 Response Body: {json.dumps(response_data, indent=2)}")
        except:
            print(f"📥 Raw Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ Email service working!")
        else:
            print(f"❌ Email service failed with status: {response.status_code}")
            
    except requests.exceptions.Timeout:
        print("❌ Request timeout - email service might be hanging")
    except requests.exceptions.ConnectionError:
        print("❌ Connection error")
    except Exception as e:
        print(f"❌ Test error: {str(e)}")

if __name__ == "__main__":
    test_production_email()
