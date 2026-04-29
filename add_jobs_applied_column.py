#!/usr/bin/env python3
"""
Script to add missing jobs_applied column to subscriptions table
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
from app.config import settings

def add_jobs_applied_column():
    """Add jobs_applied column to subscriptions table if it doesn't exist"""
    
    # Create database connection
    engine = create_engine(settings.DATABASE_URL)
    
    print("🔄 Adding jobs_applied column to subscriptions table...")
    
    try:
        with engine.connect() as connection:
            # Check if column already exists
            result = connection.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'subscriptions' 
                AND column_name = 'jobs_applied'
            """))
            column_exists = result.fetchone() is not None
            
            if column_exists:
                print("✅ jobs_applied column already exists!")
                return True
            
            # Add the missing column
            connection.execute(text("""
                ALTER TABLE subscriptions 
                ADD COLUMN jobs_applied INTEGER DEFAULT 0
            """))
            
            connection.commit()
            print("✅ jobs_applied column added successfully!")
            
            # Verify column was added
            result = connection.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'subscriptions' 
                AND column_name = 'jobs_applied'
            """))
            column_added = result.fetchone() is not None
            
            if column_added:
                print("✅ jobs_applied column verified in subscriptions table!")
                return True
            else:
                print("❌ Failed to verify jobs_applied column")
                return False
                
    except Exception as e:
        print(f"❌ Error adding column: {e}")
        return False

if __name__ == "__main__":
    success = add_jobs_applied_column()
    if success:
        print("\n🎉 jobs_applied column added successfully!")
    else:
        print("\n❌ Failed to add jobs_applied column")
