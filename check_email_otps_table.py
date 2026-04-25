#!/usr/bin/env python3
"""
Check if email_otps table exists and is working
"""

from app.database import SessionLocal, engine
from sqlalchemy import text, inspect
import traceback

def check_email_otps_table():
    """Check email_otps table"""
    print("🔍 Checking email_otps table...")
    
    try:
        # Check if table exists
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        if 'email_otps' in tables:
            print("✅ email_otps table exists")
            
            # Check table structure
            columns = inspector.get_columns('email_otps')
            print("\n📋 Table structure:")
            for col in columns:
                print(f"  - {col['name']} ({col['type']})")
            
            # Test insert and select
            db = SessionLocal()
            try:
                print("\n🧪 Testing table operations...")
                
                # Test insert
                db.execute(text("""
                    INSERT INTO email_otps (email, otp, purpose, expires_at, created_at) 
                    VALUES ('test@test.com', '123456', 'test', datetime('now', '+10 minutes'), datetime('now'))
                """))
                db.commit()
                print("✅ Insert test successful")
                
                # Test select
                result = db.execute(text("""
                    SELECT email, otp, purpose FROM email_otps WHERE email = 'test@test.com'
                """)).fetchone()
                
                if result:
                    print(f"✅ Select test successful: {result}")
                else:
                    print("❌ Select test failed - no data found")
                
                # Clean up
                db.execute(text("DELETE FROM email_otps WHERE email = 'test@test.com'"))
                db.commit()
                print("✅ Cleanup successful")
                
            except Exception as e:
                print(f"❌ Table operation error: {e}")
                traceback.print_exc()
                db.rollback()
            finally:
                db.close()
                
        else:
            print("❌ email_otps table does not exist")
            print(f"📋 Available tables: {tables}")
            
    except Exception as e:
        print(f"❌ Database check error: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    check_email_otps_table()