"""
Test job application endpoint
"""
import requests
import json

# API Configuration
BASE_URL = "https://jobnect-backend-python.onrender.com/api/v10"

def test_job_application():
    """Test the job application endpoint"""
    
    print("=" * 60)
    print("TESTING JOB APPLICATION ENDPOINT")
    print("=" * 60)
    
    # First, let's test if the API is up
    print("\n1. Testing API health...")
    try:
        response = requests.get("https://jobnect-backend-python.onrender.com/")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return
    
    # Test login to get a token
    print("\n2. Testing login...")
    login_data = {
        "email": "test@example.com",
        "password": "password123"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/login",
            json=login_data,
            headers={"Content-Type": "application/json"}
        )
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                token = result.get("data", {}).get("token")
                print(f"   ✅ Login successful")
                print(f"   Token: {token[:20]}...")
                
                # Test job application
                print("\n3. Testing job application...")
                app_data = {
                    "job_id": 1,
                    "cover_letter": "Test application"
                }
                
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {token}"
                }
                
                response = requests.post(
                    f"{BASE_URL}/applicant/job-apply",
                    json=app_data,
                    headers=headers
                )
                
                print(f"   Status: {response.status_code}")
                print(f"   Response: {json.dumps(response.json(), indent=2)}")
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get("success"):
                        print("   ✅ Application submitted successfully!")
                    else:
                        print(f"   ❌ Application failed: {result.get('message')}")
                else:
                    print(f"   ❌ HTTP Error: {response.status_code}")
            else:
                print(f"   ❌ Login failed: {result.get('message')}")
        else:
            print(f"   ❌ Login HTTP error: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    test_job_application()
