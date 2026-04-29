#!/usr/bin/env python3
"""
Test API with simpler endpoints to isolate the issue
"""

import requests
import json

def test_simple_endpoints():
    """Test simple API endpoints to see what's working"""
    print("🧪 Testing Simple API Endpoints...")
    print("-" * 50)
    
    base_url = "https://jobnect-backend-production.up.railway.app"
    
    # Test endpoints that don't involve email service
    endpoints = [
        {
            "name": "Root Endpoint",
            "url": f"{base_url}/",
            "method": "GET"
        },
        {
            "name": "Login Endpoint (without email service)",
            "url": f"{base_url}/api/v10/login",
            "method": "POST",
            "data": {
                "email": "test@example.com",
                "password": "wrongpassword"
            }
        },
        {
            "name": "Jobs Endpoint",
            "url": f"{base_url}/api/v10/jobs/recent",
            "method": "GET"
        },
        {
            "name": "Categories Endpoint",
            "url": f"{base_url}/api/v10/job-category",
            "method": "GET"
        }
    ]
    
    for endpoint in endpoints:
        try:
            print(f"\n📡 Testing: {endpoint['name']}")
            print(f"   URL: {endpoint['url']}")
            
            if endpoint['method'] == 'GET':
                response = requests.get(endpoint['url'], timeout=5)
            else:
                response = requests.post(endpoint['url'], json=endpoint['data'], timeout=5)
            
            print(f"✅ Status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"📥 Response: {json.dumps(data, indent=2)[:200]}...")
                except:
                    print(f"📥 Response: {response.text[:200]}...")
            else:
                print(f"❌ Error: {response.text[:200]}")
                
        except requests.exceptions.Timeout:
            print("❌ Timeout")
        except requests.exceptions.ConnectionError:
            print("❌ Connection error")
        except Exception as e:
            print(f"❌ Error: {str(e)}")
        
        print("-" * 30)

if __name__ == "__main__":
    test_simple_endpoints()
