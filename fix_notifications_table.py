"""
Fix notifications table - add job_seeker_id and company_user_id columns
if they don't already exist.
"""
import os
import psycopg2
from urllib.parse import urlparse

DATABASE_URL = os.environ.get("DATABASE_URL", "")

if not DATABASE_URL:
    print("ERROR: DATABASE_URL environment variable not set")
    exit(1)

# Parse the URL
parsed = urlparse(DATABASE_URL)

conn = psycopg2.connect(
    host=parsed.hostname,
    port=parsed.port or 5432,
    dbname=parsed.path.lstrip("/"),
    user=parsed.username,
    password=parsed.password,
    sslmode="require"
)
conn.autocommit = True
cur = conn.cursor()

# Check existing columns
cur.execute("""
    SELECT column_name FROM information_schema.columns
    WHERE table_name = 'notifications'
""")
existing = {row[0] for row in cur.fetchall()}
print(f"Existing columns: {existing}")

# Add missing columns
migrations = [
    ("job_seeker_id", "ALTER TABLE notifications ADD COLUMN job_seeker_id INTEGER REFERENCES job_seekers(id) ON DELETE CASCADE"),
    ("company_user_id", "ALTER TABLE notifications ADD COLUMN company_user_id INTEGER REFERENCES company_users(id) ON DELETE CASCADE"),
]

for col, sql in migrations:
    if col not in existing:
        print(f"Adding column: {col}")
        cur.execute(sql)
        print(f"  Done.")
    else:
        print(f"Column already exists: {col}")

# Create index for faster lookups
for col in ["job_seeker_id", "company_user_id"]:
    idx = f"ix_notifications_{col}"
    cur.execute(f"""
        SELECT 1 FROM pg_indexes
        WHERE tablename = 'notifications' AND indexname = '{idx}'
    """)
    if not cur.fetchone():
        cur.execute(f"CREATE INDEX {idx} ON notifications({col})")
        print(f"Created index: {idx}")

cur.close()
conn.close()
print("\nDone. Notifications table is up to date.")
