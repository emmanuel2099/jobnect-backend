#!/usr/bin/env python3
"""
Clear all payment data and restore to original state
"""
import sys
import os

# Add the app directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from sqlalchemy import text

def clear_payments():
    db = SessionLocal()
    
    try:
        print("🔄 Clearing all payment data...")
        
        # Clear all payments
        db.execute(text("DELETE FROM payments"))
        db.commit()
        
        print("✅ All payment data cleared successfully!")
        print("💡 Admin dashboard will now show ₦0 for all revenue metrics.")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    
    finally:
        db.close()

if __name__ == "__main__":
    clear_payments()