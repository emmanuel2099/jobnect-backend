"""
Keep-alive script to prevent Render free tier from sleeping.
Run this on a separate service (like cron-job.org or UptimeRobot)
"""

import requests
import time

BACKEND_URL = "https://jobnect-backend.onrender.com/api/v10/health"

def ping_backend():
    try:
        response = requests.get(BACKEND_URL, timeout=10)
        if response.status_code == 200:
            print(f"✅ Backend is awake: {response.json()}")
        else:
            print(f"⚠️  Backend responded with status {response.status_code}")
    except Exception as e:
        print(f"❌ Failed to ping backend: {e}")

if __name__ == "__main__":
    while True:
        ping_backend()
        # Wait 10 minutes before next ping
        time.sleep(600)
