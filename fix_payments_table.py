"""Fix payments table - add missing job_seeker_id and company_user_id columns"""
import os
import psycopg2

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    print("ERROR: DATABASE_URL not set")
    exit(1)

conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

fixes = [
    ("job_seeker_id", "ALTER TABLE payments ADD COLUMN job_seeker_id INTEGER REFERENCES job_seekers(id) ON DELETE CASCADE;"),
    ("company_user_id", "ALTER TABLE payments ADD COLUMN company_user_id INTEGER REFERENCES company_users(id) ON DELETE CASCADE;"),
]

for col_name, sql in fixes:
    cur.execute("""
        SELECT column_name FROM information_schema.columns
        WHERE table_name='payments' AND column_name=%s;
    """, (col_name,))
    if not cur.fetchone():
        print(f"Adding {col_name} to payments table...")
        cur.execute(sql)
        conn.commit()
        print(f"✅ {col_name} added")
    else:
        print(f"✅ {col_name} already exists")

cur.close()
conn.close()
print("Done!")
