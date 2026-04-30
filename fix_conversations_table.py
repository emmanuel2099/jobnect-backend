"""
Add missing columns to conversations and messages tables
"""
import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("❌ DATABASE_URL not found in environment")
    exit(1)

print("🔧 Fixing conversations and messages tables...")
print("=" * 60)

engine = create_engine(DATABASE_URL)

with engine.connect() as conn:
    # Check if conversations table exists
    result = conn.execute(text("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_name = 'conversations'
        );
    """))
    
    if not result.fetchone()[0]:
        print("❌ conversations table doesn't exist")
        exit(1)
    
    print("✅ conversations table exists")
    
    # Add missing columns to conversations table
    columns_to_add = [
        ("job_seeker1_id", "INTEGER REFERENCES job_seekers(id) ON DELETE CASCADE"),
        ("job_seeker2_id", "INTEGER REFERENCES job_seekers(id) ON DELETE CASCADE"),
        ("company_user1_id", "INTEGER REFERENCES company_users(id) ON DELETE CASCADE"),
        ("company_user2_id", "INTEGER REFERENCES company_users(id) ON DELETE CASCADE"),
    ]
    
    print("\n📋 Adding missing columns to conversations table...")
    for col_name, col_type in columns_to_add:
        # Check if column exists
        result = conn.execute(text(f"""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='conversations' AND column_name='{col_name}';
        """))
        
        if result.fetchone():
            print(f"   ✅ {col_name} already exists")
        else:
            try:
                conn.execute(text(f"""
                    ALTER TABLE conversations 
                    ADD COLUMN {col_name} {col_type};
                """))
                conn.commit()
                print(f"   ✅ Added {col_name}")
            except Exception as e:
                print(f"   ❌ Error adding {col_name}: {e}")
                conn.rollback()
    
    # Add missing columns to messages table
    print("\n📋 Adding missing columns to messages table...")
    
    # Check if messages table exists
    result = conn.execute(text("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_name = 'messages'
        );
    """))
    
    if not result.fetchone()[0]:
        print("❌ messages table doesn't exist")
    else:
        print("✅ messages table exists")
        
        message_columns = [
            ("job_seeker_sender_id", "INTEGER REFERENCES job_seekers(id) ON DELETE CASCADE"),
            ("job_seeker_receiver_id", "INTEGER REFERENCES job_seekers(id) ON DELETE CASCADE"),
            ("company_user_sender_id", "INTEGER REFERENCES company_users(id) ON DELETE CASCADE"),
            ("company_user_receiver_id", "INTEGER REFERENCES company_users(id) ON DELETE CASCADE"),
        ]
        
        for col_name, col_type in message_columns:
            # Check if column exists
            result = conn.execute(text(f"""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='messages' AND column_name='{col_name}';
            """))
            
            if result.fetchone():
                print(f"   ✅ {col_name} already exists")
            else:
                try:
                    conn.execute(text(f"""
                        ALTER TABLE messages 
                        ADD COLUMN {col_name} {col_type};
                    """))
                    conn.commit()
                    print(f"   ✅ Added {col_name}")
                except Exception as e:
                    print(f"   ❌ Error adding {col_name}: {e}")
                    conn.rollback()

print("\n" + "=" * 60)
print("✅ Migration complete!")
print("\nNext: Deploy this to Render:")
print("1. Commit: git add . && git commit -m 'Add migration for conversations'")
print("2. Push: git push origin main")
print("3. Run on Render: python fix_conversations_table.py")
