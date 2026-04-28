#!/usr/bin/env python3
"""
Script to create subscription tables in the existing database
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.config import settings
from app.models import Base, SubscriptionPlan, Subscription

def create_subscription_tables():
    """Create subscription tables in the database"""
    
    # Create database connection
    engine = create_engine(settings.DATABASE_URL)
    
    print("🔄 Creating subscription tables...")
    
    try:
        # Create only the subscription tables
        SubscriptionPlan.__table__.create(engine, checkfirst=True)
        Subscription.__table__.create(engine, checkfirst=True)
        
        print("✅ Subscription tables created successfully!")
        
        # Verify tables exist
        with engine.connect() as connection:
            result = connection.execute(text("""
                SELECT table_name FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name IN ('subscription_plans', 'subscriptions')
            """))
            tables = [row[0] for row in result]
            
            print(f"📋 Found tables: {tables}")
            
            if 'subscription_plans' in tables and 'subscriptions' in tables:
                print("✅ Both subscription tables are ready!")
                return True
            else:
                print("❌ Not all tables were created")
                return False
                
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        return False

if __name__ == "__main__":
    success = create_subscription_tables()
    if success:
        print("\n🎉 Ready to initialize subscription plans!")
    else:
        print("\n❌ Failed to create tables")
