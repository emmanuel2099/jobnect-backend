#!/usr/bin/env python3
"""
Reset all payments to zero - remove all dummy/test data
This ensures admin dashboard shows ₦0 revenue until real payments are made
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.config import settings

def reset_payments():
    """Reset all payments to zero"""
    
    # Get database URL
    database_url = settings.DATABASE_URL
    
    # Create engine and session
    engine = create_engine(database_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        print("🔄 Resetting all payment data to zero...")
        
        # Delete ALL payments (dummy and test data)
        result = db.execute(text("DELETE FROM payments"))
        deleted_count = result.rowcount
        
        # Reset any auto-increment counter
        try:
            db.execute(text("ALTER SEQUENCE payments_id_seq RESTART WITH 1"))
        except:
            pass  # Not all databases support this
        
        # Commit the changes
        db.commit()
        
        print(f"✅ Successfully deleted {deleted_count} payment records")
        print("💰 Admin dashboard should now show:")
        print("   - Total Revenue: ₦0")
        print("   - Monthly Revenue: ₦0") 
        print("   - Weekly Revenue: ₦0")
        print("   - Average Payment: ₦0")
        print("   - Total Payments: 0")
        print("   - Completed Payments: 0")
        print("   - Pending Payments: 0")
        print("   - Failed Payments: 0")
        
        print("\n🎯 Your app is now ready for REAL user payments!")
        print("📱 When users make actual payments through the app, they will show up here.")
        
        # Verify the reset worked
        result = db.execute(text("SELECT COUNT(*) FROM payments"))
        remaining_count = result.fetchone()[0]
        
        if remaining_count == 0:
            print(f"\n✅ VERIFICATION: Payments table is empty ({remaining_count} records)")
        else:
            print(f"\n⚠️  WARNING: Still {remaining_count} payments remaining")
        
    except Exception as e:
        print(f"❌ Error resetting payments: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    reset_payments()