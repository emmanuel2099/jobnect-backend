"""Fix email_otps table - add missing purpose column"""
import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

try:
    # Check existing columns
    cur.execute("""
        SELECT column_name FROM information_schema.columns 
        WHERE table_name = 'email_otps'
    """)
    cols = [r[0] for r in cur.fetchall()]
    print("Existing columns:", cols)

    if 'purpose' not in cols:
        cur.execute("ALTER TABLE email_otps ADD COLUMN purpose VARCHAR(50) DEFAULT 'email_verification'")
        print("✅ Added purpose column")
    else:
        print("✅ purpose column already exists")

    if 'expires_at' not in cols:
        cur.execute("ALTER TABLE email_otps ADD COLUMN expires_at TIMESTAMP DEFAULT (NOW() + INTERVAL '10 minutes')")
        print("✅ Added expires_at column")
    else:
        print("✅ expires_at column already exists")

    conn.commit()
    print("Done!")
except Exception as e:
    conn.rollback()
    print(f"Error: {e}")
finally:
    cur.close()
    conn.close()
