#!/usr/bin/env python3
"""
Check what's actually in the payments table
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.config import settings

def check_payments():
    """Check what payments are in the database"""
    
    # Get database URL
    database_url = settings.DATABASE_URL
    
    # Create engine and session
    engine = create_engine(database_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        print("💰 Checking payments table...")
        
        # Check if payments table exists
        result = db.execute(text("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'payments'
            );
        """))
        table_exists = result.fetchone()[0]
        
        if not table_exists:
            print("❌ Payments table does not exist")
            return
        
        # Count total payments
        result = db.execute(text("SELECT COUNT(*) FROM payments"))
        total_count = result.fetchone()[0]
        
        print(f"📊 Total payments in database: {total_count}")
        
        if total_count > 0:
            # Show all payments
            result = db.execute(text("""
                SELECT id, user_id, amount, currency, status, payment_method, 
                       transaction_reference, created_at 
                FROM payments 
                ORDER BY created_at DESC
            """))
            
            payments = result.fetchall()
            
            print("\n💳 Current payments:")
            for payment in payments:
                print(f"  ID: {payment[0]}, User: {payment[1]}, Amount: {payment[2]}, Status: {payment[4]}")
        else:
            print("✅ No payments found - admin dashboard should show ₦0 revenue")
        
    except Exception as e:
        print(f"❌ Error checking payments: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_payments()