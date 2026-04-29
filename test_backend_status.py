#!/usr/bin/env python3
"""
Test if backend is running at all
"""

import requests
import time

def test_backend_status():
    """Test various endpoints to see if backend is running"""
    print("🧪 Testing Backend Status...")
    print("-" * 50)
    
    base_url = "https://jobnect-backend-production.up.railway.app"
    
    endpoints = [
        "/",
        "/health",
        "/api/v10/",
        "/api/v10/health"
    ]
    
    for endpoint in endpoints:
        try:
            url = f"{base_url}{endpoint}"
            print(f"📡 Testing: {url}")
            
            response = requests.get(url, timeout=3)
            print(f"✅ Status: {response.status_code}")
            
            if response.status_code == 200:
                print(f"📥 Response: {response.text[:200]}...")
                
        except requests.exceptions.Timeout:
            print("❌ Timeout")
        except requests.exceptions.ConnectionError:
            print("❌ Connection error")
        except Exception as e:
            print(f"❌ Error: {str(e)}")
        
        print("-" * 30)
        time.sleep(0.5)

if __name__ == "__main__":
    test_backend_status()
