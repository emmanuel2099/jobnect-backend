#!/usr/bin/env python3
"""
Clear all dummy/test payment data from the database
This will remove all existing payments so only real user transactions show up
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.config import settings

def clear_dummy_payments():
    """Clear all dummy payment data from the database"""
    
    # Get database URL
    database_url = settings.DATABASE_URL
    
    # Create engine and session
    engine = create_engine(database_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        print("🗑️  Clearing all dummy payment data...")
        
        # Delete all payments (they are all dummy data)
        result = db.execute(text("DELETE FROM payments"))
        deleted_count = result.rowcount
        
        # Commit the changes
        db.commit()
        
        print(f"✅ Successfully deleted {deleted_count} dummy payment records")
        print("📊 Admin dashboard will now show only real user transactions")
        print("💰 Revenue totals will be ₦0 until real payments are made")
        
    except Exception as e:
        print(f"❌ Error clearing payments: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    clear_dummy_payments()