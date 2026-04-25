#!/usr/bin/env python3
"""
Create email_otps table for storing email verification codes
"""

import sqlite3
from datetime import datetime

def create_email_otp_table():
    """Create the email_otps table"""
    try:
        # Connect to database
        conn = sqlite3.connect('jobnect.db')
        cursor = conn.cursor()
        
        # Create email_otps table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS email_otps (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL,
                otp TEXT NOT NULL,
                purpose TEXT DEFAULT 'email_verification',
                expires_at TIMESTAMP NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create index separately
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_email_purpose 
            ON email_otps (email, purpose)
        ''')
        
        conn.commit()
        print("✅ email_otps table created successfully!")
        
        # Show table structure
        cursor.execute("PRAGMA table_info(email_otps)")
        columns = cursor.fetchall()
        
        print("\n📋 Table Structure:")
        for col in columns:
            print(f"  - {col[1]} ({col[2]})")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error creating table: {e}")

if __name__ == "__main__":
    create_email_otp_table()