#!/usr/bin/env python3
"""
Add session invalidation table to track deleted users
This allows immediate logout when admin deletes a user
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.config import settings

def add_session_invalidation_table():
    """Add session invalidation table"""
    
    # Get database URL
    database_url = settings.DATABASE_URL
    
    # Create engine and session
    engine = create_engine(database_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        print("🔄 Adding session invalidation table...")
        
        # Create invalidated_sessions table
        db.execute(text("""
            CREATE TABLE IF NOT EXISTS invalidated_sessions (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL,
                invalidated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                reason VARCHAR(255) DEFAULT 'user_deleted'
            )
        """))
        
        # Create index for faster lookups
        db.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_invalidated_sessions_user_id 
            ON invalidated_sessions(user_id)
        """))
        
        db.commit()
        
        print("✅ Successfully created invalidated_sessions table")
        print("📱 Users will now be automatically logged out when admin deletes them")
        
    except Exception as e:
        print(f"❌ Error creating table: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    add_session_invalidation_table()