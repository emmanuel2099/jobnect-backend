#!/usr/bin/env python3
"""
Test database connection to Railway
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import get_db

def test_database_connection():
    """Test database connection"""
    print("🧪 Testing Database Connection...")
    print("-" * 50)
    
    try:
        print("📡 Testing get_db() function...")
        db = next(get_db())
        print("✅ Database connection successful!")
        
        # Test a simple query
        from sqlalchemy import text
        result = db.execute(text("SELECT 1 as test")).fetchone()
        print(f"📥 Test query result: {result}")
        
        db.close()
        print("✅ Database connection closed successfully!")
        
    except Exception as e:
        print(f"❌ Database connection failed: {str(e)}")
        import traceback
        print(f"❌ Traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    test_database_connection()
