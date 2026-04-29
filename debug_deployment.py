"""
Debug script to test deployed backend and identify issues
"""

import requests
import json

def test_deployed_backend():
    """Test deployed backend and provide detailed error information"""
    
    base_url = "https://jobnect-backend-production.up.railway.app/api/v10"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    print("🔍 Testing Deployed Backend...")
    
    # Test root endpoint
    try:
        response = requests.get(f"{base_url.replace('/api/v10', '')}")
        print(f"Root endpoint status: {response.status_code}")
        if response.status_code == 200:
            print(f"Root response: {response.text[:200]}...")
        else:
            print(f"Root error: {response.text[:200]}...")
    except Exception as e:
        print(f"Root test error: {e}")
    
    # Test categories endpoint
    try:
        response = requests.get(f"{base_url}/job-category", headers=headers)
        print(f"Categories endpoint status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Categories response: {json.dumps(data, indent=2)[:300]}...")
        else:
            print(f"Categories error: {response.text[:300]}...")
    except Exception as e:
        print(f"Categories test error: {e}")
    
    # Test recent jobs endpoint
    try:
        response = requests.get(f"{base_url}/jobs/recent", headers=headers)
        print(f"Recent jobs endpoint status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Jobs response: {json.dumps(data, indent=2)[:300]}...")
        else:
            print(f"Jobs error: {response.text[:300]}...")
    except Exception as e:
        print(f"Jobs test error: {e}")

if __name__ == "__main__":
    test_deployed_backend()
