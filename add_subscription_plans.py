#!/usr/bin/env python3
"""
Script to add subscription plans to the database
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import SubscriptionPlan
from app.config import settings

def add_subscription_plans():
    # Create database connection
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Check if plans already exist
        existing_plans = db.query(SubscriptionPlan).all()
        if existing_plans:
            print(f"Found {len(existing_plans)} existing plans:")
            for plan in existing_plans:
                print(f"  - {plan.name} ({plan.tier}) - ₦{plan.price}")
            
            response = input("Do you want to delete existing plans and recreate them? (y/n): ")
            if response.lower() != 'y':
                print("Keeping existing plans.")
                return
            
            # Delete existing plans
            db.query(SubscriptionPlan).delete()
            db.commit()
            print("Deleted existing plans.")
        
        # Add new subscription plans
        plans = [
            SubscriptionPlan(
                name="Low Tier",
                tier="low",
                duration_months=1,
                description="Basic access with limited features",
                is_active=True
            ),
            SubscriptionPlan(
                name="High Tier", 
                tier="high",
                duration_months=1,
                description="Premium access with all features",
                is_active=True
            )
        ]
        
        for plan in plans:
            db.add(plan)
        
        db.commit()
        
        print("Successfully added subscription plans:")
        for plan in plans:
            job_seeker_price = 3000 if plan.tier == "low" else 10000
            company_price = 10000 if plan.tier == "low" else 20000
            print(f"  - {plan.name} ({plan.tier})")
            print(f"    Job Seekers: ₦{job_seeker_price:,}")
            print(f"    Companies: ₦{company_price:,}")
            print(f"    Duration: {plan.duration_months} month(s)")
            print(f"    Description: {plan.description}")
            print()
        
        print("Plans added successfully!")
        
    except Exception as e:
        print(f"Error adding plans: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    add_subscription_plans()
