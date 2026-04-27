#!/usr/bin/env python3
"""
Fix email_otps table for Railway deployment
"""
import os
from sqlalchemy import text
from app.database import SessionLocal, engine

def create_email_otps_table():
    """Create email_otps table if it doesn't exist"""
    print("🔧 Checking and creating email_otps table...")
    
    db = SessionLocal()
    try:
        # Check if table exists
        result = db.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_name = 'email_otps'
        """)).fetchone()
        
        if result:
            print("✅ email_otps table already exists")
            return True
        
        # Create the table (PostgreSQL compatible)
        print("🔄 Creating email_otps table...")
        db.execute(text("""
            CREATE TABLE email_otps (
                id SERIAL PRIMARY KEY,
                email VARCHAR(255) NOT NULL,
                otp VARCHAR(10) NOT NULL,
                purpose VARCHAR(50) DEFAULT 'email_verification',
                expires_at TIMESTAMP NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))
        
        # Create indexes separately
        db.execute(text("CREATE INDEX idx_email_purpose ON email_otps (email, purpose)"))
        db.execute(text("CREATE INDEX idx_expires_at ON email_otps (expires_at)"))
        db.commit()
        print("✅ email_otps table created successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error creating email_otps table: {e}")
        db.rollback()
        return False
    finally:
        db.close()

def test_email_otps_operations():
    """Test basic operations on email_otps table"""
    print("\n🧪 Testing email_otps table operations...")
    
    db = SessionLocal()
    try:
        # Test insert
        from datetime import datetime, timedelta
        expires_at = datetime.utcnow() + timedelta(minutes=10)
        
        db.execute(text("""
            INSERT INTO email_otps (email, otp, purpose, expires_at) 
            VALUES (:email, :otp, :purpose, :expires_at)
        """), {
            "email": "test@example.com",
            "otp": "123456",
            "purpose": "email_verification",
            "expires_at": expires_at
        })
        db.commit()
        print("✅ Insert test passed")
        
        # Test select
        result = db.execute(text("""
            SELECT email, otp, purpose FROM email_otps 
            WHERE email = :email
        """), {"email": "test@example.com"}).fetchone()
        
        if result:
            print(f"✅ Select test passed: {result[0]}, {result[1]}, {result[2]}")
        else:
            print("❌ Select test failed")
        
        # Test delete
        db.execute(text("""
            DELETE FROM email_otps WHERE email = :email
        """), {"email": "test@example.com"})
        db.commit()
        print("✅ Delete test passed")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing email_otps operations: {e}")
        db.rollback()
        return False
    finally:
        db.close()

def main():
    print("🚀 Fixing email_otps table for Railway deployment")
    print("=" * 50)
    
    # Check database connection
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        print("✅ Database connection successful")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return
    
    # Create table
    if create_email_otps_table():
        # Test operations
        if test_email_otps_operations():
            print("\n🎉 email_otps table is ready!")
            print("✅ Email verification should now work properly")
        else:
            print("\n⚠️ Table created but operations failed")
    else:
        print("\n❌ Failed to create email_otps table")

if __name__ == "__main__":
    main()