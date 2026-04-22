"""
Add city column to jobs table
"""
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')

def add_city_column():
    """Add city column to jobs table"""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        print("🔄 Adding city column to jobs table...")
        
        # Check if column already exists
        cur.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='jobs' AND column_name='city';
        """)
        
        if cur.fetchone():
            print("✅ City column already exists")
        else:
            # Add the city column
            cur.execute("""
                ALTER TABLE jobs 
                ADD COLUMN city VARCHAR(255);
            """)
            conn.commit()
            print("✅ City column added successfully")
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        if conn:
            conn.rollback()

if __name__ == "__main__":
    add_city_column()
