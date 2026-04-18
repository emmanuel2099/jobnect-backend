"""
Add skills column to resumes table
"""
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

def add_skills_column():
    """Add skills column to resumes table"""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        # Check if column exists
        cur.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='resumes' AND column_name='skills'
        """)
        
        if cur.fetchone() is None:
            print("Adding skills column to resumes table...")
            cur.execute("""
                ALTER TABLE resumes 
                ADD COLUMN skills TEXT
            """)
            conn.commit()
            print("✓ Skills column added successfully!")
        else:
            print("✓ Skills column already exists")
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    add_skills_column()
