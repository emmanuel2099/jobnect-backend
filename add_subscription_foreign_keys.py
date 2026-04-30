"""
Add job_seeker_id and company_user_id columns to subscriptions table
"""
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

def add_subscription_columns():
    """Add missing foreign key columns to subscriptions table"""
    
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        print("🔧 Adding foreign key columns to subscriptions table...")
        
        # Check if columns already exist
        cur.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'subscriptions' 
            AND column_name IN ('job_seeker_id', 'company_user_id')
        """)
        existing_columns = [row[0] for row in cur.fetchall()]
        
        if 'job_seeker_id' in existing_columns and 'company_user_id' in existing_columns:
            print("✅ Columns already exist!")
            return
        
        # Add job_seeker_id column if it doesn't exist
        if 'job_seeker_id' not in existing_columns:
            print("   Adding job_seeker_id column...")
            cur.execute("""
                ALTER TABLE subscriptions 
                ADD COLUMN job_seeker_id INTEGER 
                REFERENCES job_seekers(id) ON DELETE CASCADE
            """)
            print("   ✅ job_seeker_id column added")
        
        # Add company_user_id column if it doesn't exist
        if 'company_user_id' not in existing_columns:
            print("   Adding company_user_id column...")
            cur.execute("""
                ALTER TABLE subscriptions 
                ADD COLUMN company_user_id INTEGER 
                REFERENCES company_users(id) ON DELETE CASCADE
            """)
            print("   ✅ company_user_id column added")
        
        # Migrate existing data: populate job_seeker_id and company_user_id based on user_id
        print("\n🔄 Migrating existing subscription data...")
        
        # For applicants: set job_seeker_id from job_seekers table
        cur.execute("""
            UPDATE subscriptions s
            SET job_seeker_id = js.id
            FROM job_seekers js
            WHERE s.user_id = js.id
            AND s.job_seeker_id IS NULL
        """)
        applicant_count = cur.rowcount
        print(f"   ✅ Migrated {applicant_count} applicant subscriptions")
        
        # For companies: set company_user_id from company_users table
        cur.execute("""
            UPDATE subscriptions s
            SET company_user_id = cu.id
            FROM company_users cu
            WHERE s.user_id = cu.id
            AND s.company_user_id IS NULL
        """)
        company_count = cur.rowcount
        print(f"   ✅ Migrated {company_count} company subscriptions")
        
        # For legacy users that don't exist in new tables, keep them as is
        # They will continue to use user_id
        
        conn.commit()
        print("\n✅ Migration completed successfully!")
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    add_subscription_columns()
