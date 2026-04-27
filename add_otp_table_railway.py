#!/usr/bin/env python3
"""
Add email_otps table to Railway PostgreSQL database
"""
import requests
import json

def create_otp_table():
    """Create email_otps table via Railway backend API"""
    print("🔧 Creating email_otps table on Railway...")
    
    # Use the admin endpoint to execute SQL
    url = "https://jobnect-backend-production.up.railway.app/api/v10/admin/execute-sql"
    
    # SQL to create the email_otps table
    sql_query = """
    CREATE TABLE IF NOT EXISTS email_otps (
        id SERIAL PRIMARY KEY,
        email VARCHAR(255) NOT NULL,
        otp VARCHAR(10) NOT NULL,
        purpose VARCHAR(50) DEFAULT 'email_verification',
        expires_at TIMESTAMP NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    
    CREATE INDEX IF NOT EXISTS idx_email_purpose ON email_otps (email, purpose);
    CREATE INDEX IF NOT EXISTS idx_expires_at ON email_otps (expires_at);
    """
    
    try:
        response = requests.post(url, json={"query": sql_query}, timeout=30)
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ SUCCESS: {result}")
            return True
        else:
            print(f"❌ FAILED: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def test_otp_table():
    """Test the email_otps table by sending a verification email"""
    print("\n📧 Testing email_otps table...")
    
    url = "https://jobnect-backend-production.up.railway.app/api/v10/email/send-verification"
    
    try:
        response = requests.post(
            url,
            json={
                "email": "test@example.com",
                "name": "Test User"
            },
            timeout=30
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Email verification working!")
            print(f"Response: {json.dumps(result, indent=2)}")
            return True
        else:
            print(f"❌ Email verification failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def main():
    print("🚀 Adding email_otps Table to Railway Database")
    print("=" * 50)
    
    # Method 1: Try admin SQL endpoint
    if create_otp_table():
        print("\n✅ Table created successfully!")
        
        # Test the table
        if test_otp_table():
            print("\n🎉 SUCCESS! Email verification is now working!")
            print("✅ Your Flutter app should now go to OTP screen after signup")
        else:
            print("\n⚠️ Table created but email verification still has issues")
    else:
        print("\n❌ Failed to create table via admin endpoint")
        print("\n🔧 Alternative: Create table manually via Railway dashboard")
        print("1. Go to Railway dashboard → Database → Data")
        print("2. Click 'Query' tab")
        print("3. Run this SQL:")
        print("""
CREATE TABLE email_otps (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL,
    otp VARCHAR(10) NOT NULL,
    purpose VARCHAR(50) DEFAULT 'email_verification',
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_email_purpose ON email_otps (email, purpose);
CREATE INDEX idx_expires_at ON email_otps (expires_at);
        """)

if __name__ == "__main__":
    main()