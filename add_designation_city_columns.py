"""
Add designation and city columns to resumes table
"""
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

def add_columns():
    """Add designation and city columns to resumes table"""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        # Check if designation column exists
        cur.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='resumes' AND column_name='designation'
        """)
        
        if cur.fetchone() is None:
            print("Adding designation column to resumes table...")
            cur.execute("""
                ALTER TABLE resumes 
                ADD COLUMN designation VARCHAR(255)
            """)
            conn.commit()
            print("✓ Designation column added successfully!")
        else:
            print("✓ Designation column already exists")
        
        # Check if city column exists
        cur.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='resumes' AND column_name='city'
        """)
        
        if cur.fetchone() is None:
            print("Adding city column to resumes table...")
            cur.execute("""
                ALTER TABLE resumes 
                ADD COLUMN city VARCHAR(255)
            """)
            conn.commit()
            print("✓ City column added successfully!")
        else:
            print("✓ City column already exists")
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    add_columns()
