#!/usr/bin/env python3
"""
Add email_verified column to users table
"""

import sqlite3
from datetime import datetime

def add_email_verified_column():
    """Add email_verified column to users table"""
    try:
        # Connect to database
        conn = sqlite3.connect('jobnect.db')
        cursor = conn.cursor()
        
        # Check if column already exists
        cursor.execute("PRAGMA table_info(users)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'email_verified' not in columns:
            print("🔄 Adding email_verified column to users table...")
            
            # Add email_verified column
            cursor.execute('''
                ALTER TABLE users 
                ADD COLUMN email_verified INTEGER DEFAULT 0
            ''')
            
            conn.commit()
            print("✅ email_verified column added successfully!")
        else:
            print("✅ email_verified column already exists")
        
        # Show updated table structure
        cursor.execute("PRAGMA table_info(users)")
        columns = cursor.fetchall()
        
        print("\n📋 Updated Users Table Structure:")
        for col in columns:
            print(f"  - {col[1]} ({col[2]})")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error adding column: {e}")

if __name__ == "__main__":
    add_email_verified_column()