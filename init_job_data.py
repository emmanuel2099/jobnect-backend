"""
Script to initialize job types, job levels, and sample data
Run this to populate the database with required master data
"""

import requests
import json

def initialize_job_data():
    """Initialize job types, job levels, and categories via API"""
    
    base_url = "https://jobnect-backend-production.up.railway.app/api/v10"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    # Job Types to initialize
    job_types = [
        {"name": "FULL-TIME", "description": "Full-time employment"},
        {"name": "PART-TIME", "description": "Part-time employment"},
        {"name": "CONTRACT", "description": "Contract work"},
        {"name": "INTERNSHIP", "description": "Internship position"},
        {"name": "REMOTE", "description": "Remote work"},
        {"name": "HYBRID", "description": "Hybrid work"}
    ]
    
    # Job Levels to initialize
    job_levels = [
        {"name": "ENTRY-LEVEL", "description": "Entry level position"},
        {"name": "MID-LEVEL", "description": "Mid-level position"},
        {"name": "SENIOR-LEVEL", "description": "Senior level position"},
        {"name": "MANAGER", "description": "Manager position"},
        {"name": "DIRECTOR", "description": "Director position"},
        {"name": "EXECUTIVE", "description": "Executive position"}
    ]
    
    try:
        print("🚀 Initializing Job Types...")
        
        # Initialize job types
        for job_type in job_types:
            response = requests.post(
                f"{base_url}/admin/job-types/create",
                headers=headers,
                params=job_type
            )
            
            if response.status_code == 200:
                print(f"✅ Created job type: {job_type['name']}")
            else:
                print(f"❌ Failed to create {job_type['name']}: {response.status_code}")
        
        print("\n🚀 Initializing Job Levels...")
        
        # Initialize job levels
        for job_level in job_levels:
            response = requests.post(
                f"{base_url}/admin/job-levels/create",
                headers=headers,
                params=job_level
            )
            
            if response.status_code == 200:
                print(f"✅ Created job level: {job_level['name']}")
            else:
                print(f"❌ Failed to create {job_level['name']}: {response.status_code}")
        
        print("\n✅ Job data initialization complete!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nMake sure the backend is deployed and running")

if __name__ == "__main__":
    initialize_job_data()
