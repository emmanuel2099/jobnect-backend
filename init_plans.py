"""
Simple script to initialize subscription plans
Run this script after deploying the backend with the new initialize-plans endpoint
"""

import requests
import json

def initialize_plans():
    """Initialize subscription plans via API"""
    
    url = "https://jobnect-backend-production.up.railway.app/api/v10/subscriptions/initialize-plans"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    try:
        response = requests.post(url, headers=headers)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Successfully initialized subscription plans!")
            print("\nPlans created:")
            for plan in result.get('plans', []):
                print(f"  - {plan['name']} ({plan['tier']})")
                print(f"    Job Seekers: ₦{plan['job_seeker_price']:,}")
                print(f"    Companies: ₦{plan['company_price']:,}")
                print(f"    Duration: {plan['duration_months']} month(s)")
                print()
        else:
            print(f"❌ Failed to initialize plans: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nMake sure the backend is deployed with the initialize-plans endpoint")

if __name__ == "__main__":
    initialize_plans()
